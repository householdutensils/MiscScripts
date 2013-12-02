#!/usr/bin/python

import Queue
import httplib2
import threading
import argparse
import string
import random
import urllib2

#Defaults and Globals    
default_hport = "80"
response_test_iterations = 5
default_num_threads = 5


#Globals
good_elements = list()



class ansicolors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'


#Queue
equeue = Queue.Queue()

def get_bad_response(host, port):

    print "Detecting Bad Response"

    rand_char = string.ascii_letters + string.digits
    responses = list()

    for i in range(response_test_iterations):
        try:
            http_con = httplib2.Http()
            request_string = host + ":" + port + "/"
            request_string += "".join(random.sample(rand_char, 25))
            request_string += ".html"
            tmp_resp, content = http_con.request(request_string, "GET")
            responses.append(str(tmp_resp['status']))
        except Exception, e:
            print(ansicolors.RED),
            print e
            print(ansicolors.ENDC),
    response_set = list(set(responses))

    if len(response_set) == 1:
        print "Bad Response Found: " + response_set[0]
        return response_set[0]
    else:
        print(ansicolors.RED),
        print "Unable to find bad response after " + str(response_test_iterations) + " iterations, exiting :("        
        print(ansicolors.ENDC),
        exit()

class TestResult:
    def __init__(self):
        self.element = None
        self.response = None

class ElementTest(threading.Thread):
    def __init__(self, element_queue, test_host, test_port, bad_response):
        threading.Thread.__init__(self)
        self.element_queue = element_queue
        self.test_host = test_host
        self.test_port = test_port
        self.bad_response = bad_response
        
    def run(self):
        while True:
            try:
                element = self.element_queue.get(True, 2)
            except:
                element = None
            if element is None:
                break  
            
            request_string = self.test_host + ":" + self.test_port + "/"
            request_string += element
 
            try:
                resp = urllib2.urlopen(request_string)
                status_code = resp.code
            except urllib2.HTTPError, e:
                status_code = str(e.code)
            except Exception,e:
                print e

            if status_code != self.bad_response:
                tmp_result = TestResult()
                tmp_result.element = element
                tmp_result.response = status_code
                good_elements.append(tmp_result)

            self.element_queue.task_done()

def get_word_list(words_file):
    with open(words_file) as file_handle:
        words_array = file_handle.readlines()
    return words_array


def main():

    parser = argparse.ArgumentParser(description="Web Content Brute Forcer")
    parser.add_argument('-w', '--wordfile', help='File containing words to use for content testing')
    parser.add_argument('-p', '--port', help='Port to connect over (Default 80)', type=int)
    parser.add_argument('-v', '--verbose', help='Incrase verbosity')
    parser.add_argument('-t', '--threads', help='Number of worker threads to use (Default 5)')
    
    parser.add_argument('host')

    args = parser.parse_args()

    words_file = None
    if args.wordfile is not None:
        words_file = args.wordfile
    
    if args.port is not None:
        hport = args.port
    else:
        hport = default_hport

    if args.threads is not None:
        num_threads = args.threads
    else:
        num_threads = default_num_threads        


    if 'http://' in args.host or 'https://' in args.host:
        hhost = args.host
    else:
        hhost = 'http://' + args.host 
    

    bad_response = get_bad_response(hhost, hport)

    num_threads = default_num_threads

    print "Loading wordlist"

    if words_file is None:
        words_array = ['admin', 'administrator', 'test', 'secret', 'phpmyadmin', 'secret', 'manage']
    else:
        words_array = get_word_list(words_file)

    print "Loaded: " + str(len(words_array)) + " words"


    for word in words_array:
        equeue.put(word)

    if len(words_array) < num_threads:
        num_threads = len(words_array)

    print "Beginning Brute"

    thread_list = list()
    for i in range(num_threads):
        tmp_thread = ElementTest(equeue, hhost, hport, bad_response)
        tmp_thread.setDaemon(True)
        tmp_thread.start()
        thread_list.append(tmp_thread)

    equeue.join()

    for thread in thread_list:
        thread.join()
            
    print("Outputing result " + ansicolors.GREEN)
    for result in good_elements:
        print(result.element.strip('\r\n') + " " + str(result.response))
    print(ansicolors.ENDC),


if __name__ == "__main__":
    main()
