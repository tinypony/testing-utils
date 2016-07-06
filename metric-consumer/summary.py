#!/usr/bin/python

import os
import argparse
import re 

def cumulative_moving_average(new_value, old_mean, total_items):
	return old_mean + (new_value - old_mean) / total_items

def print_file_summary(path):
	cma = 0
	n = 0

	with open(path, 'r') as csv_file:
		all_lines = csv_file.readlines()
	
		for line in all_lines[1:]:
			try:
				values = line.split(',')
				#latency,1467792005016000000,3,False,338,False,256.0,1.467791983851e+12
				receive_time = float(values[1])
				send_time = float(values[7])
				receive_time = receive_time/1000000 #convert from nanoseconds
				travel_time = receive_time - send_time
				cma = cumulative_moving_average(travel_time, cma, n+1)
				n = n+1
			except:
				continue
			
	print '{} = mean {}'.format(path, cma)

parser = argparse.ArgumentParser(description='Traverse all csv files in given dir and print mean travel time')
parser.add_argument('--dir', dest='dir', type=str, help='Root directory')
parser.set_defaults(dir='.')
args = parser.parse_args()

csv_pattern = re.compile(".*\.csv$")

for root, dirs, files in os.walk(args.dir):
	
	for f in files:
		if(csv_pattern.match(f)):
        		print_file_summary('{}/{}'.format(root, f))						

