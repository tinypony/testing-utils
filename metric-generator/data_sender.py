import socket
import sys
import random 

HOST, PORT = "192.168.1.201", 1447
path = sys.argv[1]

with open(path, 'r') as f:
	random.seed(1337)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	lines = f.readlines()

	while True:
		random_line = lines[ random.randint(0, len(lines) - 1) ]
		random_line = random_line.rstrip('\n')
		# As you can see, there is no connect() call; UDP has no connections.
		# Instead, data is directly sent to the recipient via sendto().
		sock.sendto(random_line, (HOST, PORT))
