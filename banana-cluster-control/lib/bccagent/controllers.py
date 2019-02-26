'''
Contains main application logic
'''

# built-in
import inspect
import pprint
import os
import time

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
        self.str_path_pid = self.dict_config[constants.CFG_SECT_INTERNAL]['path_pid']
        self.str_path_log = self.dict_config[constants.CFG_SECT_INTERNAL]['path_log']
        #
        self.str_listen_host = self.dict_config[constants.CFG_SECT_INTERNAL]['host']
        self.int_listen_port = int(self.dict_config[constants.CFG_SECT_INTERNAL]['port'])
        #
        self.int_debug = int(self.dict_config[constants.CFG_SECT_INTERNAL]['debug'])
    #/def

    def run(self, str_action):
        '''
        Start/stop/restart/check status
        :param str_action:
        :return: bool based on the outcome of the action
        '''
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        if str_action == 'start':
            return self._start()
        elif str_action == 'stop':
            return self._stop()
        elif str_action == 'restart':
            return self._restart()
        elif str_action == 'status':
            return self._status()
        #/if
        return
    #/def

    def _start(self):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        dict_state, int_pid = self._get_status()
        str_state, str_state_val = dict_state.popitem()
        if str_state == constants.STATE_OFF: # SHUTDOWN
            pinfo("starting %r..." % self.str_nm)
            return self._start_server(int_debug=self.int_debug)
        else:
            pinfo("cannot start %r; it is already in %s state (PID=%s)" %
                  (self.str_nm, str_state_val, int_pid))
        #/if
    #/def

    def _start_server(self, int_debug=0):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        list_cmd = [self.str_path_start]
        if int_debug:
            list_cmd.append("-d")
        try:
            int_pid, _ = utils.execute(list_cmd, str_log_path=self.str_path_log, bool_nohup=True, bool_wait=False)
            # since node manager takes a while to start, we're going to temporarily insert the parent pid first
            utils.update_pid_file(int_pid=int_pid, str_path_pid=self.str_path_pid)
            return True
        except IOError, e:
            perr(e.args[0])
        return False
    #/def

    def _stop(self):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        dict_state, int_pid = self._get_status()
        str_state, str_state_val = dict_state.popitem()
        if str_state == constants.STATE_ON: # RUNNING
            pinfo("stopping %r..." % self.str_nm)
            return self._stop_server(int_pid)
        else:
            pinfo("cannot stop %r; it is already in %s state" %
                  (self.str_nm, str_state_val))
    #/def

    def _stop_server(self, int_pid, int_kill_level=2):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        os.kill(int_pid, int_kill_level)
        return True
    #/def

    def _restart(self):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        dict_state, int_pid = self._get_status()
        str_state, str_state_val = dict_state.popitem()
        if str_state == constants.STATE_ON: # RUNNING
            self._stop()
            while not self._status():
                time.sleep(1)
            return self._start()
        elif str_state == constants.STATE_OFF: # SHUTDOWN
            return self._start()
        else:
            pinfo("please try again in a bit; %r is already in %s state" %
                  (self.str_nm, str_state_val))
            return False
    #/def

    def _status(self):
        self.console.debug("%r is in %r state" % (self.str_nm, str_state))
        print "%s:%s" % (self.str_nm, str_state_val)
        if str_state == constants.STATE_ON: # "RUNNING"
            return True
        return False
    #/def

    def _get_status(self):
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