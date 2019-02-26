'''
Contains main application logic
'''

# built-in
import inspect
import pprint

# custom
from . import constants
from lib.common import utils
from lib.common.term import *

class Action:
    def __init__(self, dict_config, console):
        self.dict_config = dict_config
        self.console = console
        #
        self.str_nm = constants.SHORT_NAME
        self.str_path_start = self.dict_config[constants.CFG_SECT_INTERNAL]['path_start']
        self.str_path_stop = self.dict_config[constants.CFG_SECT_INTERNAL]['path_stop']
        self.str_path_pid = self.dict_config[constants.CFG_SECT_INTERNAL]['path_pid']
        #
        self.str_listen_host = self.dict_config[constants.CFG_SECT_INTERNAL]['host']
        self.int_listen_port = int(self.dict_config[constants.CFG_SECT_INTERNAL]['port'])
    #/def

    def run(self, str_action):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        dict_state, int_pid = self._status()
        str_state, str_state_val = dict_state.popitem()
        if str_action == 'start':
            if str_state == constants.STATE_OFF: # SHUTDOWN
                pinfo("starting '%s'..." % self.str_nm)
                return self._start()
            else:
                pinfo("cannot start '%s'; it is already in %s state (PID=%s)" %
                      (self.str_nm, str_state_val, int_pid))
        elif str_action == 'stop':
            if str_state == constants.STATE_ON: # RUNNING
                pinfo("stopping '%s'..." % self.str_nm)
                return self._stop()
            else:
                pinfo("cannot stop '%s'; it is already in %s state" %
                      (self.str_nm, str_state_val))
        elif str_action == 'status':
            self.console.debug("%r is in %r state" % (self.str_nm, str_state))
            print "%s:%s" % (self.str_nm, str_state_val)
            if str_state == constants.STATE_ON: # "RUNNING"
                return True
            else:
                return False
        #/fi
        return False
    #/def

    def _start(self):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        try:
            int_pid, _ = utils.execute([self.str_path_start], bool_nohup=True, bool_wait=False)
            # since node manager takes a while to start, we're going to temporarily insert the parent pid first
            utils.update_pid_file(int_pid=int_pid, str_path_pid=self.str_path_pid)
            return True
        except IOError, e:
            perr(e.args[0])
        return False
    #/def

    def _stop(self):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        try:
            utils.execute([self.str_path_stop], bool_wait=False)
            #if utils.kill_pid(int_pid, "-2"):
            #    utils.delete_pid_file(self.str_path_pid)
        except IOError, e:
            perr(e.args[0])
        return False
    #/def

    def _status(self):
        '''
        Return the state of the node manager's process along with its PID if available
        :return: dict_state (e.g. {"RUNNING": pred("RUNNING"}, int_pid
        '''
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        bool_found, int_pid = utils.get_pid(self.str_path_pid)
        if bool_found:
            if utils.port_listening(str_host=self.str_listen_host, int_port=self.int_listen_port):
                return {constants.STATE_ON: pgreen(constants.STATE_ON)}, int_pid # "RUNNING"
            return {constants.STATE_BUSY_ON: pyellow(constants.STATE_BUSY_ON)},int_pid # "STARTING"
        return {constants.STATE_OFF: pred(constants.STATE_OFF)},int_pid # "SHUTDOWN"
    #/def