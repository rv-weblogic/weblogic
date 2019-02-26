
# custom
import lib
from lib import utils

from lib.term import *

class Nm:
    def __init__(self, config, console):
        """
        Constructor for the configuration parser
        :param exe_basename: (str) path to the exe file
        :param console: logger
        :return:
        """
        self.dict_config = config
        self.console = console

    def perform(self, str_action):
        bool_running_state, str_pid_str = self.__status_nm__()
        if str_action == "start":
            if not bool_running_state:
                pinfo("Starting node_manager...")
                self.__start_nm__()
            else:
                pinfo("node_manager is already running. PID=%s" % str_pid_str)
        if str_action == "stop":
            if bool_running_state:
                pinfo("Stopping node_manager...")
                self.__stop_nm__()
            else:
                pinfo("node_manager is not running")
        if str_action == "status":
            if bool_running_state:
                print "(%s) node_manager" % pgreen("RUNNING")
            else:
                print "(%s) node_manager" % pred("OFFLINE")

    def __start_nm__(self):
        list_cmd = [self.dict_config["internal"]["node_manager_start"]]
        str_log = self.dict_config["internal"]["node_manager_log"]
        utils.execute(list_cmd, str_log=str_log, bool_nohup=True)

    def __stop_nm__(self):
        list_cmd = [self.dict_config["internal"]["node_manager_stop"]]
        str_log = self.dict_config["internal"]["node_manager_log"]
        utils.execute(list_cmd, str_log=str_log, bool_nohup=True)

    def __status_nm__(self):
        """
        Get the status of node manager
        :return: bool (true for running; false, not), str_pid
        """
        str_pid_file = self.dict_config["internal"]["node_manager_pid"]
        self.console.debug("Is 'node_manager' running? Checking '%s'" % str_pid_file)
        try:
            f = open(str_pid_file, 'r')
            str_pid = f.read()
            if utils.kill_pid(str_pid, "-1"):
                f.close()
                return True, str_pid
        except IOError:
            self.console.debug("node_manager's PID file '%s' is not found" % str_pid_file)
            pass
        return False, ""