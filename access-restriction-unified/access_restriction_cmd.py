import logging
import optparse

import ar_log.log as ar_log
import ar_config.config as ar_config
import ar_cmd.cmd as ar_cmd
from win32com.shell import shell

import sys,os

__author__ = "Hieu Pham"
__version__ = "1.1"
__release_notes__ ='''
[1.0]
- Initial release
[1.1]
- Cleaned up view.py
'''

def get_opt():
    """
    Parse the application's startup parameters
    :return: tuple(OptionParser, OptionParser.Values, list(left-over))
    """
    parser = optparse.OptionParser(
        usage = "%prog -c config.ini [enable|disable]",
        version = "%prog " + __version__
    )
    # parser.add_option("--debug", help="Enable debug mode.",
    #                   action="store_const", dest="debug",
    #                   const=logging.DEBUG, default=logging.INFO)

    parser.add_option("-c", "--config", help="use this configuration file",
                      dest="config")

    opt, argv = parser.parse_args()
    return parser, opt, argv

if __name__ == "__main__":
    """
    Main entrance of the application
    """
    # parse the arguments
    parser, opt, arg = get_opt()

    debug_level = logging.INFO
    if os.environ.setdefault("AR_DEBUG", "0") == "1":
        debug_level = logging.DEBUG

    # "console" will be the main debugger
    console = ar_log.create_logger(level=debug_level, name="console")
    console.debug('Verbose level set at "{}"'.format(logging.getLevelName(debug_level)))

    if len(arg) != 1:
        parser.print_help()
        sys.exit(1)

    config = ar_config.Config(file_path=opt.config, console=console)

    if not shell.IsUserAnAdmin() and not config.dict_config["internal"]["local_admin_override"]:
        console.error("This application requires local admin privileges.")
        sys.exit(1)

    batch = ar_cmd.Cmd(config=config, console=console)
    try:
        batch.do(arg[0])
    except Exception as e:
        console.error(e)


