import socket
import sys
import random 
import argparse
from time import time, sleep


def generate_influxdb_data(args):
	retval = []
	for n in range(args.number):
		data_point = 'latency,cluster={},multistack={},rate={}'.format(args.cluster_size, args.multistack, args.rate)
		retval.append(data_point)
	return retval

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


def rate_limit(data, bandwidth_or_burst, steady_state_bandwidth=None):
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

	for thing in data:
		rate_limiter.consume(len(str(thing)))
		yield thing


parser = argparse.ArgumentParser(description='Starts generating dumb metrics and sending them to monitoring client at given rate')
parser.add_argument('--cluster-size', required=True, dest='cluster_size', type=int, help='The number of kafka brokers in datasink')
parser.add_argument('--multistack', dest='multistack', help='Flag to indicate if testing bridged cloud installation')
parser.add_argument('--rate', required=True, dest='rate', type=float, help='Transmission rate of metrics in kBs')
parser.add_argument('--number', required=True, dest='number', type=int, help='The amount of metrics to generate')
parser.set_defaults(multistack=False)

args = parser.parse_args()

required_byte_rate = args.rate * 1024
HOST, PORT = "127.0.0.1", 9876
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = generate_influxdb_data(args)
for dp in rate_limit(data, required_byte_rate):
	millis = int(round(time() * 1000))
	payload = dp + ' sentat={}'.format(millis)
	sock.sendto(payload, (HOST, PORT))