import Printer
class Client:
	def __init__(self, socket, team):
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

	def addChars(self, charsAdded):
		self.charactersCount += charsAdded

	def getCharactersCount(self):
		return self.charactersCount
	def getTeamName(self):
		return self.teamName
	def getTeam(self):
		return self.team
	
	def recv(self, bufferSize):
		try:
			return self.socket.recv(bufferSize).decode('utf-8')
		except:
			return None
	
	def send(self, message):
		try:
			self.socket.sendall(bytes(message, 'utf-8'))
		except:
			return

	def endConnection(self):
		self.socket.close()


