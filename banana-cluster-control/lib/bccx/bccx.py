'''
Main
'''

# built-in
import logging, os, sys
import pprint
import signal

# custom
from . import constants
from . import gui
from . import control
from lib.common import cfg
from lib.common import log
from lib.common import utils
from lib.common import crypto
from lib.common.term import perr

#console = log.get("console")
utils.init()

# def signal_handler(signal, frame):
#     sys.stderr.write('WTF BBQ')
#     sys.stderr.write("\n<< exiting on user cancellation >>\n")
#     sys.exit(1) # instead of os._exit(1) in utils.py
# #/def
#
# utils.catch_signal(handler=signal_handler)

def main():
    str_usage = '%prog [options] [start|stop|status] [all|wls_app[1|2|...]...]'
    str_usage += '\n\nStart, stop, or check the status of Weblogic Application Servers'
    str_version =  '%s %s' % (constants.FRIENDLY_FULLNAME, constants.VERSION)
    parser, opt, argv = utils.get_opts(str_usage=str_usage, str_version=str_version)
    #
    # "console" will be the main debugger
    console = log.create(level=opt.debug, name=constants.LOGGING_NAME)
    #
    # parse the config file
    str_abs_rootdir = os.path.dirname(os.path.realpath(sys.argv[0])) # /dir
    console.debug ("str_abs_rootdir=%r" % str_abs_rootdir)
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
    control.deploy_terminfo(dict_config[constants.CFG_SECT_INTERNAL]['path_terminfo'])
    control.set_shell_env(path_dialog_lib=dict_config[constants.CFG_SECT_INTERNAL]['path_dialog_lib'],
                          str_env_term=dict_config[constants.CFG_SECT_INTERNAL]['env_term'])
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
    str_action = ''
    if len(argv) >= 1:
        str_action = argv[0]
    list_targets = []
    if len(argv) >= 2:
        list_targets = argv[1:]
    #
    dict_config_post = dict(
        path_bcc=dict_config[constants.CFG_SECT_INTERNAL]['path_bcc'],
        path_dialog=dict_config[constants.CFG_SECT_INTERNAL]['path_dialog'],
        refresh_rate_sec=int(dict_config[constants.CFG_SECT_INTERNAL].get('refresh_rate_sec', 2)),
        limit_heap_usage=int(dict_config[constants.CFG_SECT_THRESHOLD].get('limit_heap_usage', 90)),
        limit_hogging_thread=int(dict_config[constants.CFG_SECT_THRESHOLD].get('limit_hogging_thread', 5)),
    )
    xgui = gui.GUI(dict_config=dict_config_post, console=console)
    try:
        bool_ret = xgui.run(str_action=str_action, list_targets=list_targets)
    except IOError:
        sys.exit(1)
    except KeyboardInterrupt: # when ctrl-c is caught
        sys.exit(1)
    # /try

    console.debug("terminating with '%s'" % bool_ret)
    # let's flush the output before exiting to fix issue of empty output when piped to another app (e.g. grep)
    sys.stdout.flush()
    sys.stderr.flush()
    if not bool_ret:
        os._exit(1)
    os._exit(0)

