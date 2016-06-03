import socket
HOST, PORT = "0.0.0.0", 9876

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((HOST, PORT))

while True:
	#put to influxdb
	data, addr = sock.recvfrom(1024)
	print 'Received: ', data