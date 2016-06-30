import socket
import sys
import random 
import argparse

PORT=1447

parser = argparse.ArgumentParser(description='Send sub info to classifier')
parser.add_argument('--data', dest='data', required=True, type=str, help='Path to csv data')
parser.add_argument('--host', dest='host', required=True, type=str, help='Ip to send churn data to')
args = parser.parse_args()

with open(args.data, 'r') as f:
	random.seed(1337)
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	lines = f.readlines()

	while True:
		random_line = lines[ random.randint(0, len(lines) - 1) ]
		random_line = random_line.rstrip('\n')
		# As you can see, there is no connect() call; UDP has no connections.
		# Instead, data is directly sent to the recipient via sendto().
		sock.sendto(random_line, (args.host, PORT))
