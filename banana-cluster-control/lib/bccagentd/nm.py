
# custom
from lib.common import utils
from lib.common.term import *
from . import constants

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

    def start(self):
        list_cmd = [self.dict_config[constants.CFG_SECT_NM]["path_start"]]
        str_log_path = self.dict_config[constants.CFG_SECT_NM]["path_log"]
        utils.execute(list_cmd, str_log_path=str_log_path, bool_nohup=True, bool_wait=False)

    def stop(self):
        list_cmd = [self.dict_config[constants.CFG_SECT_NM]["path_stop"]]
        str_log_path = self.dict_config[constants.CFG_SECT_NM]["path_log"]
        utils.execute(list_cmd, str_log_path=str_log_path, bool_nohup=True, bool_wait=False)

    def status(self):
        """
        Get the status of node manager
        :return: bool (true for running; false, not), str_pid
        """
        str_pid_file = self.dict_config[constants.CFG_SECT_NM]["path_pid"]
        self.console.debug("is 'node_manager' running? checking '%s'" % str_pid_file)
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