import socket
import threading
from struct import unpack
import Printer
import tty, termios
import sys

serverPort = 12000
bufferSize = 1024

# Broadcast Message
clientPort = 13117
cookie_number = 0xfeedbeef
offer_number = 0x02

# Networks
developBroadcast = "172.1.0.0"
testBroadcast = "172.99.0.0"

team_name = 'cyberWednesday'

# get message cookie and check if it is 0xfeedbeef
# check the message type if it is 0x2
# check the server port (2 bytes)
# returns the server's port if legal
def analyzeBroadcatMessage(msg):
	try:
		cookie_offer_port = unpack('!IcH',msg)
		if (cookie_offer_port[0] == cookie_number and cookie_offer_port[1] == bytes([offer_number])):
			return cookie_offer_port[2]
		Printer.print_to_client_screen_green(f"Received unexpected broadcast message")
	except:
		Printer.print_to_client_screen_green(f"Received unexpected broadcast message")
	return

# getting a serverPort and serverIp address, trying to connect to the game
# if connect is successful, sending the server the team name as mentioned in the requirements
# if something went wrong, printing a message to the screen
def connectToGame(serverPort, serverIp):
	Printer.print_to_client_screen_green(f'Received offer from {serverIp}, attempting to connect...')

	try:
		TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		TCPClientSocket.connect((serverIp,serverPort))
		send_team_name = bytes(team_name+"\n", 'utf-8')
		TCPClientSocket.sendall(send_team_name)
		
		Printer.print_to_client_screen_green("Connected to the game")
		return TCPClientSocket
	except:
		Printer.error("Could not connect to the game")
		return None



# Gaming----------------------------------------------

# 2 threads are in the client: one is reading from the keyboard (thread) and the other (main thread) if receiving data from server
def gameOn(TCPSocket):
    #start the thread who listens to the keyboard
	thread = threading.Thread(target=typeAnything, args=(TCPSocket, ))
	thread.start()

    # the main thread receiving from server
	receiveFromServer(TCPSocket)

# this is the main thread that is receiving data from the server
# waiting to receive data, once received checks the correctness of sentence (if not None) and prints it to the screen as mentioned
def receiveFromServer(TCPSocket):
	while(1):
		try:
			sentence = TCPSocket.recv(bufferSize)

			if not sentence:
				return
			Printer.print_to_client_screen_orange(sentence.decode('utf-8'))
		except:
			return

# this is the function of the thread that is listening to the keyboard and sends all data from keyboard to the server
def typeAnything(TCPSocket):
	while(1):
		try:
			char = sys.stdin.read(1)
			TCPSocket.sendall(bytes(char, 'utf-8'))
		except:
			return

# clearing the buffer from all data inside it
def emptySocketBuffer(socket):
	socket.setblocking(False)
	while(True):
		try:
			socket.recv(bufferSize)
		except:
			break
	socket.setblocking(True)


def main():
	# Cheking if we are in develop mode
	developing = False
	if len(sys.argv) > 1 and (sys.argv)[1]=="develop":
		developing = True

	# setting the terminal to mode : no need for newline to read chars from keyboard
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	try:
		tty.setcbreak(sys.stdin.fileno())
	except:
		Printer.error("Unknown exception")


	# listening on UDP channel for broadcast message
	UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	UDPClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	try:
        # Binding out socket to a specific port so servers would be able to find the client
		UDPClientSocket.bind((developBroadcast if developing else testBroadcast, clientPort))

		Printer.print_to_client_screen_green(f'Client started, listening for offer requests...')
		
		while(1):
			# receiving broadcast message from server
			(msgFromServer, (serverIp, _)) = UDPClientSocket.recvfrom(bufferSize)
			server_port = analyzeBroadcatMessage(msgFromServer)

			if (server_port):
				# client connects to the game
				TCPSocket = connectToGame(server_port, serverIp)
				if(TCPSocket):
					gameOn(TCPSocket)
					TCPSocket.close()
					Printer.print_to_client_screen_green(f'Server disconnected, listening for offer requests...')
				else:
					Printer.print_to_client_screen_green(f'Listening for offer requests...')

				emptySocketBuffer(UDPClientSocket)	
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		UDPClientSocket.close()

if __name__ == "__main__":
	main()