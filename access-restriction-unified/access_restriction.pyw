import logging
import optparse

import ar_log.log as ar_log
import ar_config.config as ar_config
import ar_view.view as ar_view

import os,sys

__author__ = "Hieu Pham"
__version__ = "1.3"
__release_notes__ ='''
[1.0] 2016-09-13
- initial 1.0 release
- cleaned up view.py

[1.1] 2017-04-20
- added command line interface via access_restriction_cmd.exe

[1.2] 2017-05-23
- Fixed issue where lifting AR wipes out existing custom erropage settings

[1.3] 2018-01-28
- ar_view/view.py, populate_listbox method, added sorted before loading list_data
'''

def get_opt():
    """
    Parse the application's startup parameters
    :return: tuple(OptionParser, OptionParser.Values, list(left-over))
    """
    parser = optparse.OptionParser(
        usage = "%prog [options]",
        version = "%prog " + __version__
    )
    #parser.disable_interspersed_args() # prevent parsing parameters with cmd

    parser.add_option("-d", "--debug", help="Enable debug mode.",
                      action="store_const", dest="debug",
                      const=logging.DEBUG, default=logging.INFO)
    opt, argv = parser.parse_args()
    return parser, opt, argv

if __name__ == "__main__":
    """
    Main entrance of the application
    """
    # parse the arguments
    _, opt, _ = get_opt()

    # parse the config file
    # exe_basename = os.path.basename(os.path.splitext(__file__)[0])
    # access_restriction
    exe_basename =  os.path.basename(os.path.splitext(sys.argv[0])[0])

    # write debug to an external log file in Python "window" mode
    if sys.executable.endswith("{}.exe".format(exe_basename)) or \
        sys.executable.endswith("pythonw.exe"):
        sys.stdout = open(os.devnull, "w")
        error_file = "{}.debug".format(exe_basename)
        sys.stderr = open(error_file, "w")

    #
    # "console" will be the main debugger
    console = ar_log.create_logger(level=opt.debug, name="console")
    console.debug('Verbose level set at "{}"'.format(logging.getLevelName(opt.debug)))
    #
    abs_basedir = os.path.dirname(os.path.realpath(sys.argv[0])) #d:\dir1
    config_file = "{}.ini".format(exe_basename) # access_restriction.ini
    file_path = os.path.join(abs_basedir, config_file)
    config = ar_config.Config(file_path=file_path, console=console)
    #
    # console.debug('debug message')
    # console.info('info message')
    # console.warn('warn message')
    # console.error('error message')
    # console.critical('critical message')

    ar_view.main(config=config)