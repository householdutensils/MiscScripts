#!/usr/bin/python

import nmap
import subprocess
import Queue
import threading
import os
import datetime
import time
import argparse

current_datetime = str(datetime.datetime.now())

#Arguments
parser = argparse.ArgumentParser(description='Hydra/Nmap Auto Scan and Brute')
parser.add_argument('-pr', '--protocol', help='Protocol to test (Default: rdp)')
parser.add_argument('-po', '--port', help='Port to test (Default: 3389)')
parser.add_argument('-v', '--verbose', help='Increase verbosity of output', action='store_true')
parser.add_argument('-nT', '--notitle', help="Don't display the title", action='store_true')

user_mutgroup = parser.add_mutually_exclusive_group(required=True)
user_mutgroup.add_argument('-u', '--user', help='Username to test')
user_mutgroup.add_argument('-U', '--usersfile', help='File containing usernames to test')

pass_mutgroup = parser.add_mutually_exclusive_group(required=True)
pass_mutgroup.add_argument('-p', '--password', help='Password to test')
pass_mutgroup.add_argument('-P', '--passwordsfile', help='File containing passwords to test')

parser.add_argument('target', help='Target(s) CIDR or Range.')

args = parser.parse_args()


class ScanParams:
    def __init__(self):
        self.range = None
        self.protocol = None
        self.port = None

#Defaults
thread_num = 10


#Types
class proto_host:
        def __init__(self):
                self.host_name = ""
                self.host_ip = ""

class TestCase:
    def __init__(self):
        self.host = None
        self.username = None
        self.password = None

#Lists for Passwords/Usernames
users_list = list()
passwords_list = list()

if args.notitle is False:
    print("HydraAutoScan")
    print("-RootSecks")
    print("Date: " + current_datetime)

def load_list_from_file(listfile):
    with open(listfile) as file_handle:
        return_array = file_handle.readlines()
    return return_array

if args.user is not None:
    users_list.append(args.user)
elif args.usersfile is not None:
    users_list = load_list_from_file(args.usersfile)

if args.password is not None:
    passwords_list.append(args.password)
elif args.passwordsfile is not None:
    passwords_list = load_list_from_file(args.passwordsfile)


def check_protocol(proto):
    p = subprocess.Popen("hydra | grep Supported\ services", shell=True, stdout=subprocess.PIPE)
    result = p.stdout.read()
    result = result.rstrip('\n')
    result = result.rstrip('\r')
    if proto in result:
        return True
    else:
        return False

#Scan Params - init and defaults
scan_params = ScanParams()
scan_params.range = "127.0.0.1"
scan_params.protocol = "rdp"
scan_params.port = '3389'

if args.protocol is not None:
    if check_protocol(args.protocol):
        scan_params.protocol = args.protocol
    else:
        print("Hydra does not support the protocol: " + args.protocol + ":( Exiting")
        exit()

if args.port is not None:
    scan_params.port = args.port

if args.target is not None:
    scan_params.range = args.target

if args.verbose:
    print("Scanning range for " + scan_params.protocol + " Servers: " + scan_params.range)

nm = nmap.PortScanner()
nm.scan(scan_params.range, scan_params.port)

proto_hosts = list()

for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
                lport = nm[host][proto].keys()
                for port in lport:
                        if (nm[host][proto][port]['state'] == "open"):
                                
                                if args.verbose:
                                    print("Found " + scan_params.protocol + " Server: " + host)
                                
                                tmp_host = proto_host()
                                tmp_host.host_name = nm[host].hostname()
                                tmp_host.host_ip = host
                                proto_hosts.append(tmp_host)



class WeakCredScan(threading.Thread):
        def __init__(self, tqueue):
                threading.Thread.__init__(self)
                self.tqueue = tqueue

        def run(self):
                while True:
                        try:
                                target = self.tqueue.get(True, 2)
                        except Queue.Empty:
                                target = None
                        if target is None:
                                break

                        if args.verbose:
                            print("Checking Host: " + target.host.host_ip)

                        try:
                                p = subprocess.Popen("hydra -w 10 -l " + target.username + " -p " + target.password + " " + target.host.host_ip + " " + scan_params.protocol + " 2>&1 | grep host", shell=True, stdout=subprocess.PIPE)
                                result = p.stdout.read(1024)
                                result = result.rstrip('\n')
                                result = result.rstrip('\r')
                                if result != "":
                                        weak_creds.append(result)
                        except Exception, e:
                                print("Hydra scan failed: ")
                                print(e)
                        self.tqueue.task_done()


if args.verbose:
    print("Starting RDP Weak Credential Scan")

scan_queue = Queue.Queue()

weak_creds = list()
test_cases = list()

#Setting up test caes
for host in proto_hosts:
    for user in users_list:
        for password in passwords_list:
            
            if args.verbose:
                print("Adding test case: " + host.host_ip + " User: " + user.strip('\r\n') + " Password: " + password.strip('\r\n'))
            
            tmp_case = TestCase()
            tmp_case.host = host
            tmp_case.username = user.strip('\r\n')
            tmp_case.password = password.strip('\r\n')
            test_cases.append(tmp_case)


for case in test_cases:
    scan_queue.put(case)

scan_threads = list()

if len(proto_hosts) < 5:
        thread_num = len(proto_hosts)

for i in range(thread_num):
        cred_scan = WeakCredScan(scan_queue)
        cred_scan.setDaemon(True)
        cred_scan.start()
        scan_threads.append(cred_scan)

scan_queue.join()

for n in scan_threads:
        n.join()

output_message = ""

if args.verbose:
    output_message += "Here are the results of the scan for: " + current_datetime + "\r\n\r\n"

for line in weak_creds:
        output_message += line + "\r\n"

print(output_message)
