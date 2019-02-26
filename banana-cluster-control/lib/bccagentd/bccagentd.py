'''
Main
'''

# built-in
import logging, os, sys
import signal

# custom
from . import constants
from . import server
from . import control
from lib.common import log
from lib.common import utils
from lib.common import cfg
from lib.common import process
from lib.common.term import perr

console = log.get('console')
utils.init()

def signal_handler(signal, frame):
        console.debug("exiting on user cancellation; attempting to kill the children with signal %r" % signal)
        os.killpg(0, signal) # let's kill all of the children
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(1)
#/def

def main():
    #os.setpgrp()
    utils.catch_signal(handler=signal_handler, list_signals=(
        signal.SIGINT,   # ctrl-c
        signal.SIGTERM,) # signal 15
    )
    #
    str_usage = '%prog [options]'
    str_usage += '\n\nStart %s.' % constants.FRIENDLY_FULLNAME
    str_version =  '%s %s' % (constants.FRIENDLY_FULLNAME, constants.VERSION)
    parser, opt, argv = utils.get_opts(str_usage=str_usage, str_version=str_version)
    #
    if len(argv) != 0: # not expecting anything
        parser.print_help()
        sys.exit(1)
    #
    if sys.stdout.isatty(): # automatically enable debugging if not started in interactive mode
       opt.debug = True
    #
    console = log.create(level=opt.debug, name=constants.LOGGING_NAME)
    console.debug("verbose level set to %r" % logging.getLevelName(opt.debug))
    # parse the config file
    str_abs_basedir = os.path.dirname(os.path.realpath(sys.argv[0])) # /dir/bin
    str_abs_rootdir = os.path.dirname(str_abs_basedir) # /dir
    console.debug ("str_abs_rootdir = %r" % str_abs_rootdir)
    #
    str_config_path = utils.get_config_path(str_abs_rootdir,
                                            str_config_ext=constants.CONFIG_EXT,
                                            str_config_dir=constants.CONFIG_DIR)
    try:
        dict_config = cfg.parse(str_config_path)
    except IOError,e:
        perr(e)
        sys.exit(1)
    #/try
    control.config_post_processing(dict_config, str_abs_rootdir=str_abs_rootdir)
    #
    if not dict_config:
         parser.print_help()
         sys.exit(1)
    #
    list_args = [dict_config[constants.CFG_SECT_AGENT_JYTHON]['path_arg'],
                 dict_config[constants.CFG_SECT_AGENT_JYTHON]['path_ini']]
    #
    dict_config_jython = dict(
        name=constants.DAEMON_NAME,
        path_start=dict_config[constants.CFG_SECT_AGENT_JYTHON]['path_start'],
        path_pid=dict_config[constants.CFG_SECT_AGENT_JYTHON]['path_pid'],
        path_log=dict_config[constants.CFG_SECT_AGENT_JYTHON]['path_log'],
        host=dict_config[constants.CFG_SECT_AGENT_JYTHON]['host'],
        port=dict_config[constants.CFG_SECT_AGENT_JYTHON]['port'],
        args=list_args,
        signal_propagation=int(dict_config[constants.CFG_SECT_AGENT_JYTHON].get('signal_propagation', 1)),
        timeout_sec=900,
        # state_on=constants.STATE_ON,
        # state_off=constants.STATE_OFF,
        # state_busy_on=constants.STATE_BUSY_ON,
    )
    act = process.Process(dict_config=dict_config_jython, console=console, opt=opt)
    bool_ret = act.run(str_action="start") # start bccagentd.jy
    #
    if bool_ret: # only start when bccagentd.jy has fully started
        # terminate if bccagentd.jy dies
        utils.watchdog(str_path_pid=act.str_path_pid, func=lambda : os._exit(1), int_sleep_sec=5)
        serve = server.Server(dict_config=dict_config, console=console)
        serve.serve_forever()
