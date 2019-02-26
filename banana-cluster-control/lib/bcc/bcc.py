'''
Main
'''

# built-in
import logging, os, sys
import pprint

# custom
from . import constants
from . import control
from lib.common import cfg
from lib.common import utils
from lib.common.term import perr
from lib.common import crypto
from lib.common import log

utils.init()
utils.catch_signal(handler=utils.signal_handler)

def main():
    str_usage = '%prog [options] [start|stop|status|list|health|heap|hogging] [all|wls_app[1|2|...]...]'
    str_usage += '\n\nStart, stop, or check the status of Weblogic Application Servers.'
    str_usage += '\nList the names of the Weblogic Applications Servers.'
    str_usage += '\nGet the health state and heap usage of the JVM.'
    str_usage += '\nGet hogging thread count of the JVM.'
    str_usage += '\nNote: shell-style globbing is supported (e.g. "wls_*1").'
    str_version =  '%s %s' % (constants.FRIENDLY_FULLNAME, constants.VERSION)
    parser, _, _ = utils.get_opts(str_usage=str_usage, str_version=str_version, bool_defer_parsing=True)
    parser, opt, argv = control.add_opts(parser)
    #
    # encrypt/decrypt password
    if opt.encrypt:
        print crypto.encrypt(opt.encrypt)
        sys.exit(0)
    if opt.decrypt:
        print crypto.decrypt(opt.decrypt)
        sys.exit(0)
    #
    str_action = argv[0].lower() if len(argv) > 0 else ''
    if str_action not in ('start', 'stop', 'status', 'list', 'health', 'heap', 'hogging'):
        parser.print_help()
        sys.exit(1)
    #
    # if str_action != 'list' and len(argv) <= 1:
    if len(argv) <= 1:
        parser.print_help()
        sys.exit(1)
    #
    list_targets = argv[1:]
    #
    # "console" will be the main debugger
    console = log.create(level=opt.debug, name=constants.LOGGING_NAME)
    #
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
    control.config_post_processing(dict_config)
    #
    str_opts  = "verbose:%r" % logging.getLevelName(opt.debug)
    # str_opts += "blocking:%r\n" % opt.block
    # str_opts += "timeout_override:%s" % opt.timeout
    console.debug(str_opts)
    #
    if not dict_config:
        parser.print_help()
        sys.exit(1)
    #
    act = control.Action(dict_config=dict_config, console=console)
    bool_ret = act.run(str_action=str_action, list_targets=list_targets)
    console.debug("terminating with '%s'" % bool_ret)
    # let's flush the output before exiting to fix issue of empty output when piped to another app (e.g. grep)
    sys.stdout.flush()
    sys.stderr.flush()
    if not bool_ret:
        os._exit(1)
    os._exit(0)
