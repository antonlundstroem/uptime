import socket
import sys
import urllib.request
from urllib.error import HTTPError, URLError
import urllib
import threading
import time
import queue

# Do three requests? If all are 200, return as site is up. 
# Fix threading so multiple instances can be ran simultaneously...
# Read the things from a text file? Or do some other way...?


class Host():
    def __init__(self, hostname):
        self.hostname = hostname;
        self.state = ""

    def get_name(self):
        return self.format_name(self.hostname)

    def format_name(self, host):
        if "http://www." in host:
            return host
        else:
            return "http://www." + host

    def get_state(self):
        return self.state
    
    def set_state(self, state):
        self.state = state


class RequestHandler():
    def __init__(self, host):
        self.host = host
        self.queue = queue.Queue()
        self.threads_list = list()
    
    def do_request(self): 
        try:
            return urllib.request.urlopen(self.host.get_name(), timeout=5).getcode()
        except TimeoutError:
           return 408
        except socket.timeout:
            return 408
        except URLError:
            return 404
        
    def check_if_up(self):
        t = threading.Thread(target=self._check_if_up)
        t.start()

    def _check_if_up(self):
        counter = 0;
        while counter < 3:
            code = self.do_request()
            if (code != 200):
                return False
            counter = counter + 1
            time.sleep(1)

        return True


if __name__ == '__main__':
    hostname = sys.argv[1]
    host = Host(hostname)
    rq = RequestHandler(host)
    print(rq.check_if_up())
