'''
Contains commonly used functions
'''

# built-in
import os, subprocess, logging, sys
from optparse import OptionParser
import socket
import errno
import inspect
import pprint
import threading
import signal
import re

# custom
from . import log
from lib import gconstants

console = log.get('console')

def init():
    '''
    Suppress errors if logging isn't available
    :return:
    '''
    try: # pragma no cover
        import logging.NullHandler as NullHandler
    except ImportError: # pragma no cover
        class NullHandler(logging.Handler):
            def emit(self, record):
                pass
#/def

def catch_signal(handler, list_signals=(signal.SIGINT,)):
    for i in list_signals:
        signal.signal(i, handler)

def signal_handler(signal, frame):
    sys.stderr.write("\n<< exiting on user cancellation >>\n")
    os._exit(1)

# utils.watchdog(str_path_pid=act.str_path_pid, func=lambda : os._exit(1))
def watchdog(str_path_pid, func, int_sleep_sec=5):
    import time
    def task():
        _, int_pid = get_pid(str_path_pid)
        while pid_exists(int_pid, bool_quiet=True):
            time.sleep(int_sleep_sec)
        console.debug("alert: process PID %r has terminated" % int_pid)
        func()
    threading.Thread(target=task).start()

def get_opts(str_usage, str_version, bool_defer_parsing=False):
    '''
    Parse the application's parameters
    :param str_usage: help message
    :param str_version: version number
    :param bool_defer_parsing: defer parser.parse_args() to the caller
    :return: tuple(OptionParser, "values", list(leftover))
    '''
    console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    parser = OptionParser(
        usage=str_usage,
        version=str_version
        )
    parser.disable_interspersed_args() # prevent parsing parameters within cmd... I think..lol
    parser.add_option('-d', '--debug', help='enable debug mode',
                      action='store_const', const=logging.DEBUG,
                      default=logging.INFO, dest='debug')
    #
    if bool_defer_parsing:
        return parser, None, None
    #
    opt, argv = parser.parse_args()
    return parser, opt, argv
#/def

def get_config_path(str_abs_rootdir, str_config_ext=gconstants.CONFIG_EXT, str_config_dir=gconstants.CONFIG_DIR):
    console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    str_basename = os.path.basename(os.path.splitext(sys.argv[0])[0]) # abc
    str_config_file = '%s.%s' % (str_basename, str_config_ext) # abc.ini
    str_config_path = os.path.join(str_abs_rootdir, str_config_dir, str_config_file) # /dir/config/abc.ini
    return str_config_path
#/def

def get_local_ips():
    dict_ret = execute(['/usr/sbin/ifconfig', '-a'],
                       stdout=subprocess.PIPE,
                       bool_comm=True)
    str_result = dict_ret.get('stdout', '')
    if not str_result:
        return []
    pat = re.compile(r'^\s+inet\s+([\d\.]+)\s+netmask')
    list_ips = []
    for line in str_result.split("\n"):
        result = pat.match(line)
        if not result:
            continue
        if result.group(1) in ('0.0.0.0',):
            continue
        list_ips.append(result.group(1))
    return list_ips
#/def

def execute(list_cmd, stdout=None, stderr=None, stdin=None, str_input="",
             bool_shell=False, bool_wait=True, bool_comm=False, bool_nohup=False,
             bool_signal_propagation=False, str_log_path=os.devnull):
    console.debug(
        "invoking %s(%r, stdout=%r, stderr=%r, stdin=%r, str_input=%r, "
        "bool_shell=%r, bool_wait=%r, bool_comm=%r, bool_nohup=%r, "
        "bool_signal_propagation=%r, str_log_path=%r)" %
        (inspect.stack()[0][3], list_cmd, stdout, stderr, stdin, str_input,
         bool_shell, bool_wait, bool_comm, bool_nohup,
         bool_signal_propagation, str_log_path))
    #
    if not list_cmd:
        raise Exception("list_cmd is empty")
    #
    str_exe = list_cmd[0]
    if not os.path.exists(str_exe):
        raise IOError("%r does not exist" % str_exe)
    #
    if bool_nohup:
        list_cmd.insert(0, 'nohup')
    #
    preexec = None
    if not bool_signal_propagation:
        preexec = lambda : os.setpgrp()
    #
    if str_log_path != os.devnull: # write to a file instead of stdout/stderr
        open(str_log_path, "a").close()
        stdout = open(str_log_path, 'a')
        stderr = subprocess.STDOUT
    #
    process = subprocess.Popen(list_cmd,
                               stdout=stdout,
                               stderr=stderr,
                               stdin=stdin,
                               close_fds=True,
                               shell=bool_shell,
                               preexec_fn = preexec)
    #
    str_stdout, str_stderr = '', ''
    if bool_comm == False and str_input:
        process.stdin.write(str_input)
        process.stdin.close()
    elif bool_comm and str_input:
        str_stdout, str_stderr = process.communicate(str_input)
    elif bool_comm:
        str_stdout, str_stderr = process.communicate()
    #
    def __wait__(process):
        console.debug("[%s] waiting for process %r to end in the background" % (threading.currentThread(), process.pid))
        process.wait()
        console.debug("[%s] process %r has terminated" % (threading.currentThread(), process.pid))
    #/def
    #
    if bool_wait:
        console.debug("waiting for process %r to end" % (process.pid,))
        process.wait()
        console.debug("process %r has terminated" % (process.pid,))
    else: # let's wait in the background
        threading.Thread(target=__wait__, args=(process,)).start()
        # p = threading.Thread(target=lambda process: process.wait(), args=(process,))
    #/if
    dict_ret = dict(
        stdout=str_stdout,
        stderr=str_stderr,
        pid=str(process.pid),
        ret=process.returncode,
        )
    console.debug("dict_ret = %r" % dict_ret)
    #
    return dict_ret
#/def

def ensure_dir(str_file_path):
    '''
    Attempt to create directory if doesn't exist
    :param str_file_path:
    :return: None
    '''
    # console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    str_dir = os.path.dirname(str_file_path)
    if not os.path.exists(str_dir):
        console.debug("directory %r does not exist; attempting to create one" % str_dir)
        os.makedirs(str_dir)
    if not os.path.isdir(str_dir):
        raise IOError("path %r is not a directory" % str_dir)
#/def ensure_dir(str_file_path):

def update_pid_file(int_pid, str_path_pid):
    '''
    Update the pid file with the new pid number
    :param int_pid: pid number to be updated
    :param str_path_pid: pid file to be updated
    :return:
    '''
    console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    file_pid = open(str_path_pid, "w")
    file_pid.write(int_pid)
    file_pid.close()
#/def update_pid_file(int_pid, str_path_pid):

def delete_pid_file(str_pid_path):
    '''
    Delete the pid file
    :param str_pid_path:
    :return:
    '''
    console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    os.remove(str_pid_path)
#/def delete_pid_file(str_pid_path):

def get_pid(str_path_pid):
    '''
    Check if PID exists and return PID number
    :param str_path_pid: path to the pid file
    :return: bool_found, int_pid
    '''
    console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    try:
        f = open(str_path_pid, 'r')
        int_pid = int(f.read().strip())
        f.close()
        console.debug("got PID %r" % int_pid)
        # got a PID number; let's verify if it's valid
        if pid_exists(int_pid): # valid
            console.debug("PID %r is valid" % int_pid)
            return True, int_pid
        else:
            # since it's not valid, let's delete the PID file
            console.debug("PID %r is invalid" % int_pid)
            delete_pid_file(str_path_pid)
    except IOError:
        console.debug("PID file '%s' does not exist" % str_path_pid)
    return False, 0
#/def get_pid(str_path_pid):

def pid_exists(int_pid, bool_quiet=False):
    '''
    Check whether pid exists in the current process table
    :param int_pid:
    :return: bool_found
    '''
    if not bool_quiet:
        console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    if int_pid < 0:
        return False
    if int_pid == 0:
        # according to "man 2 kill" PID 0 refers to every process
        # in the process group of the calling process.
        # on certain systems 0 is a valid PID but we have no way
        # to know that in a portable fashion.
        raise ValueError("invalid PID 0")
    try:
        os.kill(int_pid, 0)
    except OSError as e:
        if e.errno == errno.ESRCH:
            # ESRCH == No such process
            return False
        elif e.errno == errno.EPERM:
            # EPERM clearly means there's a process to deny access to
            return True
        else:
            # according to "man 2 kill" possible error values are
            # (EINVAL, EPERM, ESRCH)... so this is uncharted territory
            raise
    else:
        return True
#/def pid_exists(int_pid, bool_quiet=False):

def port_listening(str_host, int_port, bool_quiet=False):
    '''
    Check whether anything listening on specific port
    :param str_host:
    :param int_port:
    :return: bool_
    '''
    console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res = sock.connect_ex((str_host, int_port))
    if res == 0:
        if not bool_quiet: console.debug("port pinging %r:%r; got '%s'" % (str_host, int_port, True))
        return True
    if not bool_quiet: console.debug("port pinging %r:%s; got '%s'" % (str_host, int_port, False))
    return False
#/def port_listening(str_host, int_port):

