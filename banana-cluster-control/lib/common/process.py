'''
Contains process logic
'''

# built-in
import inspect
import pprint
import os
import time
import sys
import signal

# custom
from lib.common import utils
from lib.common.term import *

class ProcessException(Exception):
    pass

class TimedOutException(Exception):
    pass

class Process:
    def __init__(self, dict_config, console, opt):
        self._read_config(dict_config)
        self.console = console
        self.bool_sigkill = opt.ensure_value("sigkill", False)
        self.bool_block = opt.ensure_value("block", True)
    #/def

    def _read_config(self, dict_config):
        self.str_svc_name = dict_config['name']
        self.str_path_start = dict_config['path_start']
        self.str_path_pid = dict_config['path_pid']
        self.str_path_log = dict_config['path_log']
        #
        self.str_listen_host = dict_config['host']
        self.int_listen_port = int(dict_config['port'])
        #
        self.str_state_on = dict_config.get('state_on', 'RUNNING')
        self.str_state_off = dict_config.get('state_off', 'SHUTDOWN')
        self.str_state_busy_on = dict_config.get('state_busy_on', 'BUSY')
        #
        self.bool_signal_propagation = bool(dict_config.get('signal_propagation', 0))
        #
        self.int_timeout_sec = int(dict_config.get('timeout_sec', '60'))
        self.list_cmd = [self.str_path_start]
        self.list_args = dict_config['args']
        if self.list_args:
            self.list_cmd.extend(self.list_args)
    #/def

    def run(self, str_action):
        '''
        Start, stop, restart or check status of the process and return the boolean outcome
        :param str_action:
        :return: bool (for status, returns True if in RUNNING state)
        '''
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        if str_action == 'start': return self._start()
        elif str_action == 'stop': return self._stop()
        elif str_action == 'restart': return self._restart()
        elif str_action == 'status':
            self._update_state()
            self._display_status()
            return self._is_running()
        return False
    #/def

    def _update_state(self):
        '''
        Update the PID and state of the process:
        :return: None
        '''
        dict_state, self.int_pid = self._get_status()
        self.str_state, self.str_state_val = dict_state.popitem()

    def _start(self):
        '''
        Start the server and return the boolean outcome
        :return: bool
        '''
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        self._update_state()
        if self.str_state == self.str_state_off: # SHUTDOWN
            pinfo("starting %r..." % self.str_svc_name, newline=False)
            return self._start_process()
        else:
            pinfo("cannot start %r since it's already in %s state (PID=%s)" %
                  (self.str_svc_name, self.str_state_val, self.int_pid))
        #/if
        return False
    #/def

    def _stop(self):
        '''
        Stop the server and return the boolean outcome
        :return: bool
        '''
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        self._update_state()
        if self.str_state == self.str_state_on: # RUNNING
            pinfo("stopping %r..." % self.str_svc_name, newline=False)
            return self._stop_process()
        else:
            pinfo("cannot stop %r since it's already in %s state" %
                  (self.str_svc_name, self.str_state_val))
        #/if
        return False
    #/def

    def _restart(self):
        '''
        Restart the server and return the boolean outcome
        :return: bool
        '''
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        self._update_state()
        if self.str_state == self.str_state_on: # RUNNING
            self._stop()
            while True: # wait until it's actually in SHUTDOWN state
                self._update_state()
                if self.str_state == self.str_state_off:
                    break
                self.console.debug("still not in SHUTDOWN state; let's sleep for a second and try again")
                time.sleep(2)
            return self._start()
        elif self.str_state == self.str_state_off: # SHUTDOWN
            return self._start() # already SHUTDOWN, let's start it
        else:
            pinfo("please try again in a bit; %r is in %s state" %
                  (self.str_svc_name, self.str_state_val))
        return False
    #/def

    def _start_process(self):
        '''
        Start the server and return the boolean outcome
        :return: bool
        '''
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        try:
            dict_return = utils.execute(self.list_cmd,
                                        str_log_path=self.str_path_log,
                                        bool_wait=False,
                                        bool_signal_propagation=self.bool_signal_propagation)
            utils.update_pid_file(int_pid=dict_return['pid'],
                                  str_path_pid=self.str_path_pid)
            if self.bool_block:
                for i in range(self.int_timeout_sec):
                    self._update_state()
                    if self.str_state == self.str_state_on: # RUNNING
                        break
                    # process suddenly disappears (assuming it failed to start)
                    if not self.int_pid:
                        raise ProcessException("process terminated unexpectedly")
                    time.sleep(1)
                    sys.stderr.write(".")
                else: # timed out
                    raise TimedOutException("timed out after %d sec" % self.int_timeout_sec)
                #/for
            sys.stderr.write(pgreen("OK") + "\n")
            return True
        except IOError, e: # executable not found
            sys.stderr.write(pred("FAILED") + "\n")
            perr(e.args[0])
        except ProcessException, e: # process failed to start
            sys.stderr.write(pred("FAILED") + "\n")
            perr(e.args[0])
        except TimedOutException, e: # timed out
            sys.stderr.write(pyellow("TIMEDOUT") + "\n")
            pinfo(e.args[0])
        return False
    #/def

    def _stop_process(self, int_kill_level=signal.SIGTERM):
        '''
        Shutdown the server and return the boolean outcome
        SIGKILL(9) is used if self.bool_sigkill is True or self.bool_block is False
        :param int_pid: process pid to kill
        :param int_kill_level: default to SIGTERM(15)
        :return: bool
        '''
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        if self.bool_sigkill: #  or not self.bool_block
            int_kill_level = signal.SIGKILL
            self.console.debug("upgrade kill level to %r" % int_kill_level)
        if not utils.pid_exists(self.int_pid):
            return False
        os.kill(self.int_pid, int_kill_level)
        if not self.bool_block:
            sys.stderr.write(pgreen("OK") + "\n")
            return False
        try:
            for i in range(self.int_timeout_sec):
                self._update_state()
                if self.str_state == self.str_state_off:
                    break
                time.sleep(1)
                sys.stderr.write(".")
            else: # timed out
                raise TimedOutException("timed out after %d sec" % self.int_timeout_sec)
            sys.stderr.write(pgreen("OK") + "\n")
            return True
        except TimedOutException, e: # timed out
            sys.stderr.write(pyellow("TIMEDOUT") + "\n")
            pinfo(e.args[0])
        return False
    #/def

    def _is_running(self):
        '''
        Return True if server is RUNNING; False for any other states
        :return: bool
        '''
        if self.str_state == self.str_state_on: # "RUNNING"
            return True
        return False

    def _display_status(self):
        '''
        Display the status of the process
        :return:
        '''
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        self.console.debug("%s:%s" % (self.str_svc_name, self.str_state))
        print "%s:%s" % (self.str_svc_name, self.str_state_val)
        #
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
                return {self.str_state_on: pgreen(self.str_state_on)}, int_pid # "RUNNING"
            return {self.str_state_busy_on: pyellow(self.str_state_busy_on)},int_pid # "BUSY"
        return {self.str_state_off: pred(self.str_state_off)},int_pid # "SHUTDOWN"
    #/def