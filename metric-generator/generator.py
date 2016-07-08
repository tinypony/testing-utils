import socket
import sys
import random 
import argparse
from time import time, sleep
from threading import Timer

class TokenBucket(object):
	"""An implementation of the token bucket algorithm.
	>>> bucket = TokenBucket(80, 0.5)
	>>> print bucket.consume(10)
	True
	adapted from http://code.activestate.com/recipes/511490-implementation-of-the-token-bucket-algorithm/?in=lang-python
	Not thread safe.
	"""

	__slots__ = ['capacity', '_tokens', 'fill_rate', 'timestamp']

	def __init__(self, tokens, fill_rate):
		"""tokens is the total tokens in the bucket. fill_rate is the
		rate in tokens/second that the bucket will be refilled."""
		self.capacity = float(tokens)
		self._tokens = float(tokens)
		self.fill_rate = float(fill_rate)
		self.timestamp = time()

	def consume(self, tokens, block=True):
		"""Consume tokens from the bucket. Returns True if there were
		sufficient tokens.
		If there are not enough tokens and block is True, sleeps until the
		bucket is replenished enough to satisfy the deficiency.
		If there are not enough tokens and block is False, returns False.
		It is an error to consume more tokens than the bucket capacity.
		"""

		assert tokens <= self.capacity, \
			'Attempted to consume {} tokens from a bucket with capacity {}' \
				.format(tokens, self.capacity)

		if block and tokens > self.tokens:
			deficit = tokens - self._tokens
			delay = deficit / self.fill_rate

			# print 'Have {} tokens, need {}; sleeping {} seconds'.format(self._tokens, tokens, delay)
			sleep(delay)

		if tokens <= self.tokens:
			self._tokens -= tokens
			return True
		else:
			return False

	@property
	def tokens(self):
		if self._tokens < self.capacity:
			now = time()
			delta = self.fill_rate * (now - self.timestamp)
			self._tokens = min(self.capacity, self._tokens + delta)
			self.timestamp = now
		return self._tokens


class InfiniteTokenBucket(object):
	"""TokenBucket implementation with infinite capacity, i.e. consume always
	returns True."""

	__slots__ = ()

	def __init__(self, tokens=None, fill_rate=None):
		pass

	def consume(self, tokens, block=True):
		return True

	@property
	def tokens(self):
		return float('infinity')


def rate_limit(args, bandwidth_or_burst, steady_state_bandwidth=None):
	"""Limit the bandwidth of a generator.
	Given a data generator, return a generator that yields the data at no
	higher than the specified bandwidth.  For example, ``rate_limit(data, _256k)``
	will yield from data at no higher than 256KB/s.
	The three argument form distinguishes burst from steady-state bandwidth,
	so ``rate_limit(data, _1024k, _128k)`` would allow data to be consumed at
	128KB/s with an initial burst of 1MB.
	"""

	bandwidth = steady_state_bandwidth or bandwidth_or_burst
	rate_limiter = TokenBucket(bandwidth_or_burst, bandwidth)

	for n in range(args.number):
		data_point = 'latency,id={},cluster={},multistack={},direct={},rate={} sentat=0000000000000'.format(n, args.cluster_size, args.multistack, args.direct, args.rate)
		rate_limiter.consume(len(data_point))
		yield data_point


parser = argparse.ArgumentParser(description='Starts generating dumb metrics and sending them to monitoring client at given rate')
parser.add_argument('--cluster-size', dest='cluster_size', type=int, help='The number of kafka brokers in datasink')
parser.add_argument('--multistack', dest='multistack', help='Flag to indicate if testing bridged cloud installation')
parser.add_argument('--rate', dest='rate', type=float, help='Transmission rate of metrics in kBs')
parser.add_argument('--number', dest='number', type=int, help='The amount of metrics to generate')
parser.add_argument('--direct', dest='direct', help='Indicates if messages are send directly to the consumer or through ANDy framework')
parser.add_argument('--unbound', dest='unbound', help='Indicates if messages are send constantly with no rate limiting')
parser.add_argument('--ip', dest='ip', type=str, help='The IP of the receiving endpoint')
parser.add_argument('--port', dest='port', type=int, help='The port of the receiving endpoint')
parser.add_argument('--protocol', dest='protocol', type=str, help='Protocol used to send data to the local port. tcp or udp')
parser.set_defaults(cluster_size=1)
parser.set_defaults(multistack=False)
parser.set_defaults(direct=False)
parser.set_defaults(rate=256.0)
parser.set_defaults(ip='127.0.0.1')
parser.set_defaults(port=9876)
parser.set_defaults(protocol='tcp')
parser.set_defaults(number=100)
parser.set_defaults(unbound=False)

args = parser.parse_args()
running = True
HOST, PORT = args.ip, args.port

if args.protocol == 'tcp':
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))
elif args.protocol == 'udp':
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def finish():
	running = False

def send_unbound(args, sock):
	r = Timer(61.0, finish)
	r.start()
	n = 0
	while running:
		millis = int(round(time() * 1000))
		data_point = 'latency,id={},cluster={},multistack={},direct={},rate={} sentat={}'.format(n, args.cluster_size, args.multistack, args.direct, args.rate, millis)
		n += 1
		if args.protocol == 'tcp':
			sock.send(data_point)
		elif args.protocol == 'udp':
			sock.sendto(data_point, (HOST, PORT))

	print 'I am done!'
	sock.close();


def send_with_rate_limit(args, sock):
	required_byte_rate = args.rate * 1024
	start_time = time()
	bytes_sent = 0
	messages_sent = 0

	for dp in rate_limit(args, required_byte_rate/32, required_byte_rate):
		millis = int(round(time() * 1000))
		payload = dp.replace('sentat=0000000000000', 'sentat={}\n'.format(millis))

		if args.protocol == 'tcp':
			bytes_sent += sock.send(payload)
		elif args.protocol == 'udp':
			bytes_sent += sock.sendto(payload, (HOST, PORT))

		messages_sent += 1


	end_time = time()
	time_total = end_time - start_time
	print 'Messages sent {}'.format(messages_sent)
	print 'Sent {} bytes in {} second, which translates to {} kBps rate'.format(bytes_sent, time_total, (bytes_sent/1024)/time_total)
	sock.close();

if args.unbound:
	send_unbound(args, sock)
else:
	send_with_rate_limit(args, sock)