import Printer
import socket

# this is a class that is responsible for all the functions that client performs
# in addition, we decided to create this object class to save all the data per client
# this class helps for game statistics and calculations in the server.py
class Client:
	def __init__(self, socket, team, port, ip):
		self.port = port
		self.ip = ip
		self.charactersCount = 0
		self.socket = socket
		self.team = team
		self._setTeamName()
		Printer.print_info(f"{self.teamName} as joined the game!")
		
	# Call this function only in the constructor
	def _setTeamName(self):
		# receiving teamName from TCP socket
		teamName=""
		with self.socket.makefile() as clientfile:
			c = clientfile.read(1)
			while not (c=='\n'):
				teamName=teamName+c
				c = clientfile.read(1)
		self.teamName = teamName

# given an client ipaddress and port, checking if the current client is from these addresses
	def isFrom(self, ip, port):
		return self.port == port and self.ip == ip

# given sentence from user, adding the amount of chars in sentence to the class
# keeping track of how many chars each client typed
	def addChars(self, charsAdded):
		self.charactersCount += charsAdded
# Getters--------------------------------------------------------------------------------
	def getCharactersCount(self):
		return self.charactersCount

	def getTeamName(self):
		return self.teamName

	def getTeam(self):
		return self.team
	
# getting data from client socket
	def recv(self, bufferSize):
		try:
			return self.socket.recv(bufferSize).decode('utf-8')
		except:
			return None
# sending message to this client
	def send(self, message):
		try:
			self.socket.sendall(bytes(message, 'utf-8'))
		except:
			return
# closing the connection with this client
	def endConnection(self):
		try:
			self.socket.shutdown(socket.SHUT_RDWR)
			self.socket.close()
		except:
			# client closed the connection
			self.socket.close()


