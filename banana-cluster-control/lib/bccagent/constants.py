'''
Contains constant variables
'''

from lib import gconstants

FRIENDLY_FULLNAME =  gconstants.AGENT_INIT_FULLNAME # ""Banana Cluster Control Agent Daemon Init Control"
SHORT_NAME = gconstants.AGENT_INIT_NAME # "bccagent"
DAEMON_NAME = gconstants.AGENT_DAEMON_FULLNAME # "Banana Cluster Control Daemon"
#
VERSION = gconstants.VERSION
CONFIG_EXT = gconstants.CONFIG_EXT # "ini"
CONFIG_DIR = gconstants.CONFIG_DIR # "config"
#
CFG_SECT_INTERNAL = gconstants.AGENT_INIT_NAME # "bccagent"
LOGGING_NAME = gconstants.LOGGING_NAME # "console"
#
STATE_ON = "RUNNING"
STATE_OFF = "SHUTDOWN"
STATE_BUSY_ON = "BUSY"