#!/usr/bin/python

import Queue
import threading
import os
import argparse
import socket

APP_PATH = os.path.abspath(os.path.dirname(__file__))

check_queue = Queue.Queue()
user_queue = Queue.Queue()

work_list = list()

existing_users = list()

default_thread_num = 10
default_sock_timeout = 10

class UserAcc():
    def __init__(self):
        self.user = None
        self.addr = None

class AddressChecker(threading.Thread):
    def __init__(self, tqueue, sock_timeout):
        threading.Thread.__init__(self)
        self.tqueue = tqueue
        self.sock_timeout = sock_timeout

    def check_vrfy_status(self, response):
        legit = True
        if 'VRFY disallowed' in response:
            legit = False
        
        if 'Cannot VRFY user' in response:
            legit = False

        return legit

    def run(self):
        while True:
            try:
                address = self.tqueue.get(True, 2)
            except Queue.Empty:
                address = None
            if address == None:
                break
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.sock_timeout)
                result = sock.connect_ex((address, 25))
                if result == 0:
                    address_status = True
                else:
                    address_status = False
                    sock.close()
            except:
                address_status = False
                sock.close()
            if address_status is True:
                try:
                    banner = sock.recv(1024)
                    sock.send('HELO localhost\r\n')
                    sock.recv(1024)
                    sock.send('VRFY test\r\n')
                    response = sock.recv(1024)
                    sock.close()
                    vrfy_capable = self.check_vrfy_status(response)
                    if vrfy_capable is True:
                        work_list.append(address)
                except:
                    address_status = False
            self.tqueue.task_done()

class UserChecker(threading.Thread):
    def __init__(self, uqueue, sock_timeout):
        threading.Thread.__init__(self)
        self.uqueue = uqueue
        self.sock_timeout = sock_timeout

    def check_user(self, response):
        legit = True
        if 'VRFY disallowed' in response:
            legit = False
        
        if 'Cannot VRFY user' in response:
            legit = False

        if 'User unknown' in response:
            legit = False

        return legit

    def run(self):
        while True:
            try:
                tmp_user = self.uqueue.get(True, 2)
            except:
                tmp_user = UserAcc()
            if tmp_user.user == None:
                break
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.sock_timeout)
                result = sock.connect_ex((tmp_user.addr, 25))
                if result == 0:
                    address_status = True
                else:
                    address_status = False
                    sock.close()
            except:
                address_status = False
                sock.close()
            if address_status is True:
                try:
                    banner = sock.recv(1024)
                    sock.send('HELO localhost\r\n')
                    sock.recv(1024)
                    sock.send('VRFY ' + tmp_user.user + '\r\n')
                    response = sock.recv(1024)
                    sock.close()
                    user_exists = self.check_user(response)
                    if user_exists is True:
                        existing_users.append(tmp_user)
                except:
                    address_status = False
            self.uqueue.task_done()

def get_users(usersfile):
    with open(usersfile) as file_handle:
        users_array = file_handle.readlines()
    return users_array

def parse_addresses(addresses):
    address_list = list()
    if '-' in addresses:
        address_split = addresses.split('-')
        final_addr = address_split[1]
        prefix_split = address_split[0].split('.')
        address_prefix = prefix_split[0] + '.' + prefix_split[1] + '.' + prefix_split[2]
        first_addr = prefix_split[3]
        for addr in range(int(first_addr), int(final_addr) + 1):
            tmp_address = address_prefix + '.' + str(addr)
            address_list.append(tmp_address)
    else:
        address_list.append(addresses)
    return address_list

def main():
    parser = argparse.ArgumentParser(
        description="SMTP User brute forcer")

    mutgroup = parser.add_mutually_exclusive_group(required=True)
    mutgroup.add_argument(
        '-U', '--usersfile',
        help="File containing usernames to test")
    mutgroup.add_argument(
        '-u', '--username',
        help="Single username ot test")

    parser.add_argument(
        '-t', '--threads', help="Num of threads to use", type=int)
    parser.add_argument(
        '-T', '--socktimeout', help="Custom socket timeout", type=int)

    parser.add_argument(
        'target', type=str, nargs='?',
        help="Address, range")

    args = parser.parse_args()

    if args.target is not None:
        
        if args.threads is not None:
            thread_num = args.threads
        else:
            thread_num = default_thread_num

        if args.socktimeout is not None:
            sock_timeout = args.socktimeout
        else:
            sock_timeout = default_sock_timeout
        
        if (args.usersfile is not None):
            users_array = get_users(args.usersfile)
        elif (args.username is not None):
            users_array = list()
            users_array.append(args.username)

        address_list = parse_addresses(args.target)
        
        for addr in address_list:
            check_queue.put(addr)

        cthreads = list()
        for i in range(thread_num):
            checkThread = AddressChecker(check_queue, sock_timeout)
            checkThread.setDaemon(True)
            checkThread.start()
            cthreads.append(checkThread)

        check_queue.join()

        for i in range(thread_num):
            check_queue.put(None)
        
        users_list = list()
        for addr in work_list:
            for user in users_array:
                tmp_user = UserAcc()
                tmp_user.user = user
                tmp_user.addr = addr
                user_queue.put(tmp_user)

        uthreads = list()
        for i in range(thread_num):
            userThread = UserChecker(user_queue, sock_timeout)
            userThread.setDaemon(True)
            userThread.start()
            uthreads.append(userThread)

        user_queue.join()
        
        for i in range(thread_num):
            tmp_user = UserAcc()
            user_queue.put(tmp_user)

        print "Server\t\t\tUser"
        for user in existing_users:
            print user.addr + "\t\t" + user.user,

    else:
        parser.error("You need to enter a range (Only supports the last octet) or address")

if __name__ == "__main__":
    main()
