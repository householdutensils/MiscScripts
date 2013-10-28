#!/bin/bash

DNSFILE=$1 #A file containing a list of names to try
DOMAIN=$2 #The domain to query
DNSSERVER=$3 #The DNS server to query

JOBPOOL=2 #Limit on how many jobs to spawn. This prevents a forkbomb like effect.

for name in $(cat $DNSFILE);do
	NUMJOBS=$(jobs | wc | awk ' { print $1 } ')
	while [ $NUMJOBS -gt $JOBPOOL ]
	do
		NUMJOBS=$(jobs | wc | awk ' { print $1 } ')
	done
	host $name.$DOMAIN $DNSSERVER | grep "has address" &
done
wait
