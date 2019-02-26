'''
Contains constant variables
'''

from lib import gconstants

FRIENDLY_FULLNAME =  gconstants.AGENT_DAEMON_FULLNAME #"Banana Cluster Control Agent Daemon"
SHORT_NAME = gconstants.AGENT_DAEMON_NAME # "bccagentd"
DAEMON_NAME = gconstants.AGENT_JYTHON_NAME # "bccagentd.jy"
#
VERSION = gconstants.VERSION
CONFIG_EXT = gconstants.CONFIG_EXT # "ini"
CONFIG_DIR = gconstants.CONFIG_DIR # "config"
LOGGING_NAME = gconstants.LOGGING_NAME # "console"
#
CFG_SECT_INTERNAL = gconstants.AGENT_DAEMON_NAME # "bccagentd"
CFG_SECT_AGENT_JYTHON = gconstants.AGENT_JYTHON_NAME # "bccagentd.jy"
CFG_SECT_WEBLOGIC= gconstants.WEBLOGIC_NAME # "weblogic"
CFG_SECT_NM = gconstants.NODE_MANAGER_NAME # "node_manager"

