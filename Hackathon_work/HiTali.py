import socket
import threading
from struct import unpack
import msvcrt
import Printer

serverPort = 12000
bufferSize = 1024
clientPort = 13117
team_name = 'cyberWednesday'

# get message cookie and check if it is 0xfeedbeef
# check the message type if it is 0x2
# check the server port (2 bytes)
# returns the server's port if legal


def analyzeBroadcatMessage(msg):
	cookie_offer_port = unpack('IBI',msg)
	if (cookie_offer_port[0] == 0xfeedbeef and cookie_offer_port[1] == 0x2):
		return cookie_offer_port[2]
	Printer.print_to_client_screen_green(f"Received unexpected broadcast message")
	return

def connectToGame(serverPort, serverIp):
	Printer.print_to_client_screen_green(f'Received offer from {serverIp}, attempting to connect...')

	TCPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	TCPClientSocket.connect((serverIp,serverPort))
	send_team_name = bytes(team_name+"\n", 'utf-8')
	TCPClientSocket.sendall(send_team_name)
	
	Printer.print_to_client_screen_green("Connected to the game")

	return TCPClientSocket
	

# Gaming----------------------------------------------
def gameOn(TCPSocket):
    # start the thread who listens to the keyboard
	thread = threading.Thread(target=typeAnything, args=(TCPSocket, ))
	thread.start()
    # the main thread receiving from server
	receiveFromServer(TCPSocket)
    # wait for both of threads
	thread.join()

def receiveFromServer(TCPSocket):
	with TCPSocket:
		while(1):
			try:
				sentence = TCPSocket.recv(bufferSize)
				if sentence:
					Printer.print_to_client_screen_orange(sentence.decode('utf-8'))
				else:
					return
			except:
				return

def typeAnything(TCPSocket):
	while(1):
		try:
			# change when connecting to SSH!!!!!!!!!!!!
			char = msvcrt.getche()
			# input_from_keyboard = input()
			TCPSocket.sendall(char)
		except:
			return
# -----------------------------------------------------------

def main():
	# listening on UDP channel for broadcast message
	UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
        # Binding out socket to a specific port so servers would be able to find the client
        # Maybe change '' to '<broadcast>'
		UDPClientSocket.bind(('', clientPort))

		Printer.print_to_client_screen_green(f'Client started, listening for offer requests...')
		
		while(1):
			# receiving broadcast message from server
			(msgFromServer, (serverIp, _)) = UDPClientSocket.recvfrom(bufferSize)
			server_port = analyzeBroadcatMessage(msgFromServer)

			if (server_port):
				TCPSocket = connectToGame(server_port, serverIp)
				gameOn(TCPSocket)
				TCPSocket.close()
				Printer.print_to_client_screen_green(f'Server disconnected, listening for offer requests...')
				
	except:
		UDPClientSocket.close()

if __name__ == "__main__":
	main()