#!/bin/env python
import os, subprocess
from subprocess import PIPE

def execute(list_cmd, str_log_path=os.devnull, bool_nohup=False, bool_wait=True):
    '''
    Executing a long running process
    :param str_exe: file to be exected
    :param str_log: both stdout and stderr will be redirected to this log
    :return:
    '''
    str_exe = list_cmd[0]
    if not os.path.exists(str_exe):
        raise IOError("'%s' does not exist" % str_exe)
    if bool_nohup:
        list_cmd.insert(0, 'nohup')
    open(str_log_path, "a").close()
    cmd = subprocess.Popen(list_cmd,
             stdout=open(str_log_path, 'a'),
             stderr=subprocess.STDOUT)
    print '[PID=%d] invoking execute("%s", str_log="%s", bool_nohup="%s", bool_wait="%s")' % \
          (cmd.pid, list_cmd, str_log_path, bool_nohup, bool_wait)
    if bool_wait and not bool_nohup:
        cmd.wait()
    print '[PID=%d] got return code of %s' % (cmd.pid, cmd.returncode)
    return (str(cmd.pid), str(cmd.returncode))

if __name__ == "__main__":
    sh = "python"
    log = "/tmp/xyz.log"
    open(log, "a").close()
    cmd = subprocess.Popen([sh], stdout=PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
    str_output=cmd.communicate(b'from datetime import datetime\nprint datetime.now()')
    #cmd.stdin.write(b'from datetime import datetime\nprint datetime.now()')
    cmd.wait()
    print '[PID=%d] got return code of %s' % (cmd.pid, cmd.returncode)
    print str_output[0]
    #print(open(log, 'r').read())
