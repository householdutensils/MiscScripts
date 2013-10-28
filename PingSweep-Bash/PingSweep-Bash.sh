#!/bin/bash

################################################################################################
#pingsweep.sh                                                                                   #
#                                                                                               #
#Loop through 192.168.16.0/23                                                                   #
#Ping each host in new process and grep for the IPs of the hosts that respond                   #
#Wait for all processes to finish                                                               #
#                                                                                               #
#Problems:                                                                                      #
# 1> This could be made faster by managing the timeout (-W), but it may produce false-negatives #
# 2> You need to manually manage the octets based on the network, this should be automated.     #
# 3> Because of above, there are two broadcast addresses in the range thats scanned.            #
#       currently I just redirect stderr to /dev/null...it's not an elegant solution            #
#################################################################################################


for thirdoctet in {16..17}
do
        for fourthoctet in {0..255}
        do

                ping -c 1 "192.168.${thirdoctet}.${fourthoctet}" 2> /dev/null | grep --line-buffered "bytes from" | awk '{print $4}' | cut -d ':' -f 1 &

        done
done

wait
