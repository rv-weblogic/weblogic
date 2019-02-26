from SocketServer import ThreadingMixIn
from SimpleXMLRPCServer import SimpleXMLRPCServer
import socket

import time

class MyXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        SimpleXMLRPCServer.server_bind(self)

def return_string(name):
    time.sleep(5)
    return name.upper()

def return_list(num):
    return range(num)

def return_dict(key, value):
    return dict(key=value)


server = MyXMLRPCServer(("0.0.0.0", 9999))
server.register_function(return_string, "return_string")
server.register_function(return_list, "return_list")
server.register_function(return_dict, "return_dict")
print "listening..."
server.serve_forever()