'''
Contains constant variables
'''

from lib import gconstants

FRIENDLY_FULLNAME =  gconstants.CLIENT_FULLNAME # "Banana Cluster Control Client"
SHORT_NAME = gconstants.CLIENT_NAME # "bcc"
#
VERSION = gconstants.VERSION
CONFIG_EXT = gconstants.CONFIG_EXT # "ini"
CONFIG_DIR = gconstants.CONFIG_DIR # "config"
#
LOGGING_NAME = gconstants.LOGGING_NAME # "console"
#
CFG_SECT_WEBLOGIC = gconstants.WEBLOGIC_NAME # "weblogic"
CFG_SECT_NODE_MANAGER = gconstants.NODE_MANAGER_NAME # "node_manager"
CFG_SECT_AGENT = gconstants.AGENT_DAEMON_NAME # "bccagentd"
# CFG_SECT_AGENT_JYTHON = gconstants.AGENT_JYTHON_NAME # "bccagentd.jy"