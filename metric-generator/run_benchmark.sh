#!/bin/bash
if [ -z $1 ]; then 
	echo "specify direct ip address"
	exit
fi
python generator.py --rate 256 --number 10000 --direct True --protocol udp  --port 8089 --ip $1
python generator.py --rate 512 --number 10000 --direct True --protocol udp  --port 8089 --ip $1
python generator.py --rate 1024 --number 10000 --direct True --protocol udp --port 8089 --ip $1

python generator.py --rate 256 --number 10000 --direct False  --port 9876 --ip 127.0.0.1
python generator.py --rate 512 --number 10000 --direct False  --port 9876 --ip 127.0.0.1
python generator.py --rate 1024 --number 10000 --direct False  --port 9876 --ip 127.0.0.1
