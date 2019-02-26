# built-in
import sys
import inspect
import pprint
import xmlrpclib, socket
import threading

import time
#from multiprocessing import Process
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn
from subprocess import PIPE, Popen

# custom
from lib.common.term import *
#from lib.common import utils
from . import constants
#from lib import gconstants
#
# enable multithreaded
class MultiThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass
#
class Server:
    def __init__(self, dict_config, console):
        self.dict_config = dict_config
        self.console = console
    #/def

    def terminate(self):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))

    def serve_forever(self):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))

        for i in reversed(range(4)):
            self.console.debug("starting in %ds" % i)
            time.sleep(1)

        str_listen_address = self.dict_config[constants.CFG_SECT_INTERNAL]["listen_address"]
        int_listen_port = int(self.dict_config[constants.CFG_SECT_INTERNAL]["listen_port"])
        self.console.info("bccagentd is listening on 'http://%s:%s'" %(str_listen_address, int_listen_port))
        #
        server = MultiThreadedXMLRPCServer( (str_listen_address, int_listen_port), allow_none=True)
        #
        server.register_introspection_functions()
        server.register_multicall_functions()
        server.register_instance(self)
        # server.register_function(self.get_jython_pid, "get_jython_pid")
        # server.register_function(self.terminate, "terminate")
        # server.register_function(self.execute, "execute")
        # server.register_function(self.print_me, "print_me")
        #
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            self.console.info('terminating server')
            sys.exit(1)

    # def __wait__(self, process):
    #     self.console.debug("[%s] waiting for process %d to end" % (threading.currentThread(), process.pid))
    #     process.wait()
    #     self.console.debug("[%s] process %d has terminated" % (threading.currentThread(), process.pid))
    # #/def

    # def start_wls_admin(self, *tuple_params):
    #     self.console.debug("invoking %s%s" % (inspect.stack()[0][3], tuple_params))
    #     # tuple_params = (self.dict_wls_admin["name"],
    #     #                 self.dict_node_manager["address"],
    #     #                 self.dict_node_manager["port"],
    #     #                 self.dict_wls_admin["domain"])
    #     list_params = list(tuple_params)
    #     #
    #     str_weblogic_username = self.dict_config[constants.CFG_SECT_WEBLOGIC]["username"]
    #     str_weblogic_password = self.dict_config[constants.CFG_SECT_WEBLOGIC]["password"]
    #     str_path_wlst = self.dict_config[constants.CFG_SECT_AGENT_JYTHON]["path_wlst"]
    #     str_wls_admin_name = list_params.pop(0)
    #     #
    #     list_params.insert(0, str_weblogic_password)
    #     list_params.insert(0, str_weblogic_username)
    #     #
    #     str_input = '''nmConnect%s\nnmStart(%r)\n''' % (tuple(list_params),str_wls_admin_name)
    #     #
    #     # nmConnect('soa12', 'mtogov123', '10.77.6.11', '25001', 'soa')
    #     #str_input = '''from datetime import datetime\nprint datetime.now()\n'''
    #     #
    #     self.console.debug("executing '%s' with %r" % (str_path_wlst, str_input))
    #     dict_ret = self.execute(list_cmd=[str_path_wlst], stdout=PIPE, stderr=PIPE, stdin=PIPE,
    #                             str_input=str_input, bool_wait=False, bool_comm=False, shell=False)
    #     return dict_ret

    # def execute(self, list_cmd, stdout=None, stderr=None, stdin=None,
    #                    str_input="", bool_wait=True, bool_comm=True, shell=False):
    #     self.console.debug(
    #         "invoking %s(%r, stdout=%r, stderr=%r, stdin=%r,str_input=%r, bool_wait=%r, bool_comm=%r, shell=%r)" %
    #         (inspect.stack()[0][3], list_cmd, stdout, stderr, stdin,
    #          str_input, bool_wait, bool_comm, shell))
    #     #
    #     if not list_cmd:
    #         self.console.debug("dict_ret = '%s'" % {})
    #         return {}
    #     process = Popen(list_cmd, stdout=stdout, stderr=stderr, stdin=stdin, close_fds=True, shell=shell)
    #     #
    #     str_stdout, str_stderr = '', ''
    #     if bool_comm == False and str_input:
    #         process.stdin.write(str_input)
    #         process.stdin.close()
    #     elif bool_comm and str_input:
    #         str_stdout, str_stderr = process.communicate(str_input)
    #     elif bool_comm:
    #         str_stdout, str_stderr = process.communicate()
    #     #
    #     # if not bool_comm: # force not to wait if no communcation
    #     #     bool_wait = False
    #     if bool_wait:
    #         self.console.debug("[%s] waiting for process %d to end" % (threading.currentThread(), process.pid))
    #         process.wait()
    #         self.console.debug("[%s] process %d has terminated" % (threading.currentThread(), process.pid))
    #     else:
    #         p = threading.Thread(target=self.__wait__, args=(process,))
    #         p.start()
    #
    #     dict_ret = dict(
    #         stdout=str_stdout,
    #         stderr=str_stderr,
    #         pid=str(process.pid),
    #         ret=process.returncode,
    #         )
    #     self.console.debug("dict_ret = %r" % dict_ret)
    #     #
    #     return dict_ret
    #     #return str(process.pid), str(process.returncode)

