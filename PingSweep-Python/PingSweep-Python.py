#!/usr/bin/python

import os
import Queue
import threading
import argparse
from netaddr import IPNetwork

ping_queue = Queue.Queue()
ping_thread_num = 50
output_list = list()

parser = argparse.ArgumentParser(
    description="Python Ping Sweep")

parser.add_argument(
    'target', help="CIDR For ping sweep")

args = parser.parse_args()

for ip in IPNetwork(args.target):
    ping_queue.put(str(ip))

class ansicolours:
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'

class DoPing(threading.Thread):
    def __init__(self, pqueue):
        threading.Thread.__init__(self)
        self.pqueue = pqueue

    def run(self):
        while True:
            try:
                host = self.pqueue.get(True, 2)
            except:
                host = None
            if host is None:
                break
            result = os.system('ping -c 1 ' + host + '> /dev/null 2>&1')
            if result == 0:
                output_list.append(host + "\t\t\t" + ansicolours.GREEN + "[+]" + ansicolours.ENDC)
            else:
                output_list.append(host + "\t\t\t" + ansicolours.RED + "[-]" + ansicolours.ENDC)
            self.pqueue.task_done()

output_list.append("Host\t\t\tPing Result")

ping_threads = list()
for i in range(ping_thread_num):
    pingThread = DoPing(ping_queue)
    pingThread.setDaemon(True)
    pingThread.start()
    ping_threads.append(pingThread)

ping_queue.join()

for i in range(ping_thread_num):
    ping_queue.put(None)
    
for line in output_list:
    print line