import socket
import threading
import time
from Client import Client
from Networking import Networking
from struct import pack
import Printer
from itertools import chain


serverPort = 12000
## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
ip_address = socket.gethostbyname(hostname)

# global broadcastMode
broadcastMode = False
clientGameMode = False

# Broadcast Message
bufferSize = 1024
cookie_number = 0xfeedbeef
offer_number = 0x02

clientsLists = []

team1 = "Ravidi"
team2 = "Tali"

def sendClients(message): 
	global clientsLists
	for client in clientsLists:
		client.send(message)
	Printer.print_clientMessage(f"Sent to clients:\n{message}")

# broadcasting stage ---------------------------------------------------------------------------------------------
def sendBroadcasts():
	global broadcastMode
	broadcastMode=True
	while(broadcastMode):
		message = pack('IBI',cookie_number,offer_number,serverPort)
		networking.sendBroadcast(message)
		time.sleep(0.2)

def acceptClients():
	global broadcastMode
	global clientsLists
	assignTo = team1
	while(True):
		clientSocket = networking.acceptClient()
		if(not broadcastMode):
			clientSocket.close()
		else:
			newClient = Client(clientSocket, assignTo)
			assignTo = team2 if (assignTo==team1) else team1
			clientsLists.append(newClient)
			threading.Thread(target=clientThreadGame, args=(newClient,)).start()

# gaming stage ---------------------------------------------------------------------------------------------
def getNamesByTeam(team):
	global clientsLists
	teamGroups = filter(lambda client: client.getTeam() == team, clientsLists)
	return map(lambda client: client.getTeamName(), teamGroups)

def sendWelcomeMessage():
	team1Names = getNamesByTeam(team1)
	team2Names = getNamesByTeam(team2)
	
	team1NamesToSend = '\n'.join([elem for elem in team1Names]) 
	team2NamesToSend = '\n'.join([elem for elem in team2Names]) 

	message = f"""Welcome to Keyboard Spamming Battle Royale.
Group 1:
==
{team1NamesToSend}

Group 2:
==
{team2NamesToSend}"""
	
	sendClients(message)

def clientThreadGame(client):
	global broadcastMode
	global clientGameMode
	while(clientGameMode or broadcastMode):
		sentence = client.recv(bufferSize)
		if not sentence:
			return 
		if(clientGameMode):
			client.addChars(len(sentence))

# ending stage ---------------------------------------------------------------------------------------------
def calculateWinners():
	global clientsLists
	countTeam1=0
	countTeam2=0
	winner=""
	for client in clientsLists:
		if(client.getTeam()==team1):
			countTeam1+=client.getCharactersCount()
		else:
			countTeam2+=client.getCharactersCount()
	if(countTeam1>countTeam2):
		winner=team1
	elif(countTeam2>countTeam1):
		winner=team2
	else:
		winner=None
	
	namesString ='\n'.join([elem for elem in getNamesByTeam(winner)])
	message = f"""Game over!
Group 1 typed in {countTeam1} characters. Group 2 typed in {countTeam2} characters.
Group {1 if (winner == team1) else 2} wins!
Congratulations to the winners:
==
{namesString}"""

	namesString ='\n'.join([elem for elem in chain(getNamesByTeam(team1), getNamesByTeam(team2))])
	tieMessage = f"""Game over!
Group 1 typed in {countTeam1} characters. Group 2 also typed in {countTeam2} characters!.
It's a tie :o!
Congratulations to everybody!:
==
{namesString}"""
		
	# send the end message to everybody in the game
	messageToSend = message if winner else tieMessage
	sendClients(messageToSend)

def endConnections():
	global clientsLists
	for client in clientsLists:
		client.endConnection()

def endRound():
	global clientGameMode
	global clientsLists
	clientGameMode=False
	calculateWinners()
	endConnections()
	clientsLists = []
	Printer.print_state("Game over, sending out offer requests...")

def init():
	global networking
	# Creating all the needed sockets
	networking = Networking(serverPort)

	# Starting the accept clients thread
	threading.Thread(target=acceptClients, args=()).start()
	
# Transition from waiting fot clients phase to game phase
def startGame():
	global broadcastMode
	global clientGameMode
	broadcastMode = False
	clientGameMode=True
	sendWelcomeMessage()
	Printer.print_state("Prepare yourself, the game is starting")

# Main thread ---------------------------------------------------------------------------------------------
def main():
	init()
	Printer.print_state(f'Server started, listening on IP address {ip_address}')

	while(1):
		threading.Thread(target=sendBroadcasts, args=()).start()
		time.sleep(5)
		startGame()
		time.sleep(5)
		endRound()

if __name__ == "__main__":
	main()