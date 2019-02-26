'''
Contains constant variables
'''

from lib import gconstants

FRIENDLY_FULLNAME = gconstants.NODE_MANAGER_INIT_FULLNAME # "Node Manager Daemon Init Control"
SHORT_NAME = gconstants.NODE_MANAGER_INIT_NAME # "bccnm"
DAEMON_NAME = gconstants.NODE_MANAGER_FULLNAME # "Node Manager Daemon"
#
VERSION = gconstants.VERSION
CONFIG_EXT = gconstants.CONFIG_EXT # "ini"
CONFIG_DIR = gconstants.CONFIG_DIR # "config"
#
CFG_SECT_INTERNAL = SHORT_NAME # "bccnm"
LOGGING_NAME = gconstants.LOGGING_NAME # "console"
#
STATE_ON = "RUNNING"
STATE_OFF = "SHUTDOWN"
STATE_BUSY_ON = "BUSY"