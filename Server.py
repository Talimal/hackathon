import socket
import threading
import time

import scapy
from ClientHandler import Client
from Networking import Networking
from struct import pack
import Printer
from itertools import chain

serverPort = 12000
## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
ip_address = socket.gethostbyname(hostname)
developing = False

# global broadcastMode
broadcastMode = False
clientGameMode = False

# Broadcast Message
bufferSize = 1024
cookie_number = 0xfeedbeef
offer_number = 0x02

clientsLists = []

# best player ever in the server - statistics
bestPlayerInServer=""
scoreOfBestPlayerEver=-1

# mot common char in Game - statistics
mostCommonCharPerGame=''
charsJson={}

# names od the teams in this server
team1 = "Ravidi"
team2 = "Tali"

# Helpers---------------------------------------------------------------------

# gets a sentence and updates the json which keeps track of every char and 
# it's number of times it was types

def updateMostCommonChar(sentence):
	global charsJson
	for char in sentence:
		if char not in charsJson:
			charsJson[char]=1
		else:
			charsJson[char]+=1

# sending the same message to all clients
def sendClients(message): 
	global clientsLists
	for client in clientsLists:
		client.send(message)
	Printer.print_clientMessage(f"Sent to clients:\n{message}")

# broadcasting stage ---------------------------------------------------------------------------------------------

# send broadcast message forall
def sendBroadcasts():
	global broadcastMode
	broadcastMode=True
	while(broadcastMode):
		message = pack('IBI',cookie_number,offer_number,serverPort)
		networking.sendBroadcast(message, developing)
		time.sleep(0.2)

# gets a client ip and client port and checks if client already in the game
# if so, deletes it and updated the clients list 
def removeIfExists(client_ip, client_port):
	global clientsLists
	for client in clientsLists:
		if client.isFrom(client_ip, client_port):
			clientsLists.remove(client)

# accepts client from TCP socket and creates new Client object to keep
# track of the little buddy
def acceptClients():
	global broadcastMode
	global clientsLists
	assignTo = team1
	while(True):
		(clientSocket, (client_ip, client_port)) = networking.acceptClient()
		if(not broadcastMode):
			clientSocket.close()
		else:
			removeIfExists(client_ip, client_port)
			newClient = Client(clientSocket, assignTo, client_ip, client_port)
			assignTo = team2 if (assignTo==team1) else team1
			clientsLists.append(newClient)
			threading.Thread(target=clientThreadGame, args=(newClient,)).start()
				

# gaming stage ---------------------------------------------------------------------------------------------

# as it's name, getting a team and returns all names of members in team
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
			updateMostCommonChar(sentence)

# ending stage ---------------------------------------------------------------------------------------------
def calculateWinners():
	global clientsLists
	global bestPlayerInServer
	global scoreOfBestPlayerEver
	global charsJson
	countTeam1=0
	countTeam2=0
	winner=""
	maxCharsInGame=-1
	nameOfBestPlayer=""
	
	for client in clientsLists:
		if (client.getCharactersCount()>maxCharsInGame):
			maxCharsInGame=client.getCharactersCount()
			nameOfBestPlayer=client.getTeamName()
			
		if (client.getCharactersCount()>scoreOfBestPlayerEver):
			scoreOfBestPlayerEver=client.getCharactersCount()
			bestPlayerInServer=client.getTeamName()
			
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
	
	maxTimesOfChar=0
	maxTypesChar=''
	for (char,times) in charsJson.items():
		if times > maxTimesOfChar:
			maxTimesOfChar = times
			maxTypesChar = char
	
	namesString ='\n'.join([elem for elem in getNamesByTeam(winner)])
	message = f"""Game over!
Group 1 typed in {countTeam1} characters.
Group 2 typed in {countTeam2} characters.
Group {1 if (winner == team1) else 2} wins!
Congratulations to the winners:
========
{namesString}"""

	namesString ='\n'.join([elem for elem in chain(getNamesByTeam(team1), getNamesByTeam(team2))])
	tieMessage = f"""Game over!
Group 1 typed in {countTeam1} characters.
Group 2 also typed in {countTeam2} characters.
It's a tie :o!
Congratulations to everybody!:
========
{namesString}
"""

	mostTypedChar = f"Most typed char in this game was {maxTypesChar} which was types {maxTimesOfChar} times." if maxTimesOfChar != 0 else ""
	statisticsRegular = f"""
Statistics
========
MVP group of the game is {nameOfBestPlayer} with {maxCharsInGame} charactars.
Best group of all times is {bestPlayerInServer} with {scoreOfBestPlayerEver} charactars.
{mostTypedChar}
"""
	newBestStatistics = f"""
Statistics
========
MVP group of the game and new best group of all times is {nameOfBestPlayer} with {maxCharsInGame} charactars.
{mostTypedChar}
"""
		
	# send the end message to everybody in the game
	messageToSend = message if winner else tieMessage
	statistics = newBestStatistics if maxCharsInGame >= scoreOfBestPlayerEver else statisticsRegular
	sendClients(messageToSend + statistics)

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
	global mostCommonCharPerGame
	global charsJson
	charsJson={}
	mostCommonCharPerGame=''
	broadcastMode = False
	clientGameMode=True
	sendWelcomeMessage()
	Printer.print_state("Prepare yourself, the game is starting")

def getCorrectAddress():
	global ip_address
	global developing
	mode = (sys.argv)[1]
	if mode=="test":
		developing = True
		ip_address = scapy.get_if_addr("eth1")
	else:
		ip_address = scapy.get_if_addr("eth2")

# Main thread ---------------------------------------------------------------------------------------------
def main():
	getCorrectAddress()
	init()
	Printer.print_state(f'Server started, listening on IP address {ip_address}')

	while(1):
		threading.Thread(target=sendBroadcasts, args=()).start()
		time.sleep(10)
		startGame()
		time.sleep(10)
		endRound()

if __name__ == "__main__":
	main()