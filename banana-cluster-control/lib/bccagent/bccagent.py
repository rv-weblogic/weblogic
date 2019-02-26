'''
Main
'''

# built-in
import logging, os, sys

# custom
from . import constants
from . import control
from lib.common import log
from lib.common import utils
from lib.common import cfg
from lib.common import process
from lib.common.term import perr

utils.init()
utils.catch_signal(handler=utils.signal_handler)

def main():
    str_usage = '%prog [options] [start|stop|restart|status]'
    str_usage += '\n\nStart, stop, restart or check the status of the %s.' % constants.DAEMON_NAME
    str_version =  '%s %s' % (constants.FRIENDLY_FULLNAME, constants.VERSION)
    parser, _, _ = utils.get_opts(str_usage=str_usage, str_version=str_version, bool_defer_parsing=True)
    parser, opt, argv = control.add_opts(parser)
    #
    if len(argv) != 1: # expecting an action only
        parser.print_help()
        sys.exit(1)
    #
    str_action = argv[0].lower()
    if str_action not in ('start', 'stop', 'restart', 'status'):
        parser.print_help()
        sys.exit(1)
    #
    console = log.create(level=opt.debug, name=constants.LOGGING_NAME)
    # parse the config file
    str_abs_rootdir = os.path.dirname(os.path.realpath(sys.argv[0])) # /dir
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
    if opt.timeout <= 0:
        opt.timeout = dict_config[constants.CFG_SECT_INTERNAL].get('timeout_sec', 60)
    #
    str_opts  = "verbose:%r\n" % logging.getLevelName(opt.debug)
    str_opts += "blocking:%r\n" % opt.block
    str_opts += "timeout_override:%s" % opt.timeout
    console.debug(str_opts)
    #
    dict_config_post = dict(
        name=constants.DAEMON_NAME,
        path_start=dict_config[constants.CFG_SECT_INTERNAL]['path_start'],
        path_pid=dict_config[constants.CFG_SECT_INTERNAL]['path_pid'],
        path_log=dict_config[constants.CFG_SECT_INTERNAL]['path_log'],
        host=dict_config[constants.CFG_SECT_INTERNAL]['ping_host'],
        port=dict_config[constants.CFG_SECT_INTERNAL]['ping_port'],
        args=dict_config[constants.CFG_SECT_INTERNAL].get('args', '').split(),
        timeout_sec=opt.timeout,
        state_on=constants.STATE_ON,
        state_off=constants.STATE_OFF,
        state_busy_on=constants.STATE_BUSY_ON,
    )
    act = process.Process(dict_config=dict_config_post, console=console, opt=opt)
    bool_ret = act.run(str_action=str_action)
    console.debug("terminating with '%s'" % bool_ret)
    # let's flush the output before exiting to fix issue of empty output when piped to another app (e.g. grep)
    sys.stdout.flush()
    sys.stderr.flush()
    if not bool_ret:
        os._exit(1) # sys.exit() waits for all threads to finish
    os._exit(0)
