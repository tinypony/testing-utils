#!/bin/bash
rm ./direct/*.csv
rm $1/*.csv

if [ -z $1 ]; then
  echo 'must provide root folder'
  exit
fi

influx -database performance -format csv -execute "SELECT * FROM latency WHERE direct = 'True' AND rate = '256.0'" > direct/rate256.csv
influx -database performance -format csv -execute "SELECT * FROM latency WHERE direct = 'True' AND rate = '512.0'" > direct/rate512.csv
influx -database performance -format csv -execute "SELECT * FROM latency WHERE direct = 'True' AND rate = '1024.0'" > direct/rate1024.csv
influx -database performance -format csv -execute "SELECT * FROM latency WHERE direct = 'False' AND rate = '256.0'" > $1/indirect_rate256.csv
influx -database performance -format csv -execute "SELECT * FROM latency WHERE direct = 'False' AND rate = '512.0'" > $1/indirect_rate512.csv
influx -database performance -format csv -execute "SELECT * FROM latency WHERE direct = 'False' AND rate = '1024.0'" > $1/indirect_rate1024.csv

influx -database performance -execute 'DROP MEASUREMENT latency'
