
# built-in
import os
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn

# custom
from lib import utils
from lib.term import *
import lib

# enable multithreaded
class MultiThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class Action:
    def __init__(self, dict_config, console):
        self.dict_config = dict_config
        self.console = console

    def perform(self, str_action):
        bool_running_state, str_pid_str = self.__status_server__()
        if str_action == "start":
            if not bool_running_state:
                pinfo("Starting %s..." % lib.SERVER_NAME)
                self.__start_server__()
            else:
                pinfo("%s is already running. PID=%s" % (lib.SERVER_NAME, str_pid_str))
        if str_action == "stop":
            if bool_running_state:
                pinfo("Stopping %s..." % lib.SERVER_NAME)
                self.__stop_server__()
            else:
                pinfo("%s is not running" % lib.SERVER_NAME)
        if str_action == "status":
            if bool_running_state:
                print "(%s) %s" % (pgreen("RUNNING"), lib.SERVER_NAME)
            else:
                print "(%s) %s" % (pred("OFFLINE"), lib.SERVER_NAME)

    def __start_server__(self):
        # list_cmd = [
        #     self.dict_config["internal"]["wlst_script"],
        #     self.dict_config["internal"]["server_binary"],
        #     self.dict_config["__self_path__"],
        #     self.dict_config["internal"]["pid_path"],
        #     ]
        # str_log = self.dict_config["internal"]["log_path"]
        # utils.execute(list_cmd, str_log=str_log, bool_nohup=True)

    def __stop_server__(self):
        # bool_running, str_pid = self.__status_server__()
        # if not bool_running:
        #     return
        # bool_ret = utils.kill_pid(str_pid, str_level="-TERM")
        # self.console.debug("Got '%s'" % bool_ret)

    def __status_server__(self):
        """
        Get the status of node manager
        :return: bool (true for running; false, not), str_pid
        """
        # str_pid_file = self.dict_config["internal"]["pid_path"]
        # self.console.debug("Is '%s' running? Checking '%s'" % (lib.SERVER_NAME, str_pid_file))
        # try:
        #     f = open(str_pid_file, 'r')
        #     str_pid = f.read()
        #     if utils.kill_pid(str_pid, "-1"):
        #         f.close()
        #         return True, str_pid
        # except IOError:
        #     self.console.debug("%s's PID file '%s' is not found" % (lib.SERVER_NAME, str_pid_file))
        #     pass
        # return False, ""