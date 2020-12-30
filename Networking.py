import socket

clientBroadcastPort = 13117
developBroadcast = "172.1.255.255"
testBroadcast = "172.99.255.255"

class Networking:
	def __init__(self, serverPort):
		self.createServerTCPSocket(serverPort)
		self.createBroadcastSocket()
	
	def createServerTCPSocket(self, serverPort):
		# opening TCP socket so that new clients can connect us
		#TCP server socket
		self.TCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.TCPSocket.bind(('', serverPort))
		self.TCPSocket.listen()


	def acceptClient(self):
		clientSocket, address = self.TCPSocket.accept()
		return (clientSocket, address)


	def createBroadcastSocket(self):
		# opening new UDP socket to send broadcast messages
		# UDP server socket
		self.BroadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# Enable port reusage so we will be able to run multiple clients and servers on single (host, port). 
		# https://gist.github.com/ninedraft/7c47282f8b53ac015c1e326fffb664b5#gistcomment-3091801
		self.BroadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# Enable broadcasting mode
		self.BroadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	def sendBroadcast(self, message, developing):
		self.BroadcastSocket.sendto(message, (developBroadcast if developing else testBroadcast, clientBroadcastPort))
		# self.BroadcastSocket.sendto(message, ("255.255.255.255", clientBroadcastPort))

