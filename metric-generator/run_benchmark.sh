#!/bin/bash
if [ -z $1 ]; then
        echo "specify direct ip address"
        exit
fi

if [ -z $2 ]; then
        echo "specify cluster size"
        exit
fi

python generator.py --rate 256 --number 10000 --direct True --protocol udp  --port 8089 --ip $1
python generator.py --rate 512 --number 10000 --direct True --protocol udp  --port 8089 --ip $1
python generator.py --rate 1024 --number 10000 --direct True --protocol udp --port 8089 --ip $1
python generator.py --rate 2048 --number 10000 --direct True --protocol udp --port 8089 --ip $1

python generator.py --rate 256 --number 10000 --direct False --cluster-size $2  --port 9876 --ip 127.0.0.1
python generator.py --rate 512 --number 10000 --direct False --cluster-size $2  --port 9876 --ip 127.0.0.1
python generator.py --rate 1024 --number 10000 --direct False --cluster-size $2  --port 9876 --ip 127.0.0.1
python generator.py --rate 2048 --number 10000 --direct False --cluster-size $2  --port 9876 --ip 127.0.0.1
