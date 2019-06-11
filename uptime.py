import socket
import sys
import urllib.request
from urllib.error import HTTPError, URLError
import urllib
import threading
import time
import queue
import os
from enum import Enum

# Do three requests? If all are 200, return as site is up. 
# Fix threading so multiple instances can be ran simultaneously...
# Read the things from a text file? Or do some other way...?

class State(Enum):
    UP = "UP"
    DOWN = "DOWN"


class Host():
    def __init__(self, hostname):
        self.hostname = hostname;
        self.state = ""

    def get_name(self):
        return self.format_name(self.hostname)

    def format_name(self, host):
        if "https://www." in host:
            return host
        elif "www." in host:
            return "http://" + host
        else:
            return "http://www." + host

    def get_state(self):
        return self.state
    
    def set_state(self, State):
        self.state = State


class RequestHandler():
    def __init__(self, host):
        self.host = host
        self.queue = queue.Queue()
        self.threads_list = list()
    
    def do_request(self): 
        try:
            # Set timeout to other int when implementing, maybe make able to set personal timeout
            urllib.request.urlopen(self.host.get_name(), timeout=5).getcode() 
            self.host.set_state(State.UP)
        except TimeoutError:
            self.host.set_state(State.DOWN)

        except socket.timeout:
            self.host.set_state(State.DOWN)

        except URLError:
            self.host.set_state(State.DOWN)

    def check_if_up(self):
        counter = 0;
        while counter < 3:
            self.do_request() # Does request to the hosts url
            if (self.host.get_state() == State.DOWN): # Checks if hosts is down
                if(self.check_if_start_daemon()): # Checks if user wants to start the daemon for the host
                    self.start_thread_daemon() # Starts the daemon for the host
                    #
                    # Here the daemon should be started and maybe not return false. That is the job for the thread to return true when its back up!
                    #
                    return False
                else:
                    return False
            counter = counter + 1
            time.sleep(1)

        return True

    def check_if_start_daemon(self):
        txt = input("Webpage: " + self.host.get_name() + " seems to be down.\nDo you want to start the daemon to get notified when it comes back up?\n[y]/[n]: ")
        if (txt == "y" or txt == "yes"):
            return True
        elif (txt == "n" or txt == "no"):
            return False
        else:
            self.check_if_start_daemon()


    def start_thread_daemon(self):
        t = threading.Thread(target=self.daemon)
        t.start()

    def daemon(self):
        while (self.host.get_state() == State.DOWN):
            print("doing daemon")
            self.do_request()
            time.sleep(10) # Set another value for the interval for which the daemon should be run, perhaps every minute?


class CheckUptime():
    def run(self, hostname):
        host = Host(hostname)
        req = RequestHandler(host)
        print("\nChecking webpage: " + host.get_name())
        
        if (req.check_if_up()):
            host.set_state(State.UP)
            print(host.get_name() + " is up!")
            os.system("/usr/bin/notify-send " + host.get_name() + " " + str(host.get_state().value))

        else:
            host.set_state(State.DOWN)



if __name__ == '__main__':
    for i in range (len(sys.argv)-1):
        CheckUptime().run(sys.argv[i+1])
