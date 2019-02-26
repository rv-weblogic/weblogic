
# built-in
import xmlrpclib, socket, sys
import inspect
import pprint
import fnmatch

# custom
from . import constants
from lib import gconstants
from lib.common.term import *
from lib.common import utils
from lib.common import crypto
from lib.common import log

console = log.get("console")

def add_opts(parser):
    parser.add_option('--encrypt', help='encrypt a password phrase',
                      metavar='STRING', type='str',
                      dest='encrypt')
    parser.add_option('--decrypt', help='decrypt a password phrase',
                      metavar='STRING', type='str',
                      dest='decrypt')
    parser.add_option('-r', '--raw', help='display raw data',
                      action='store_const', const=True,
                      default=False, dest='raw')
    opt, argv = parser.parse_args()
    return parser, opt, argv
#/def

def config_post_processing (dict_config, **kargs):
    '''
    Post processing. Note: side-effects
    :param dict_config: dict()
    :param kargs: dict()
    :return:
    '''
    # decrypt the password
    for str_section in dict_config.keys():
        #for str_cfg in ('path_start', 'path_ini', 'path_log', 'path_pid'):
        for str_cfg in (s for s in dict_config[str_section] if s == 'password'):
            str_password = dict_config[str_section][str_cfg]
            dict_config[str_section][str_cfg] = crypto.decrypt(str_password)
    #
    console.debug('(post) dict_config=\n%s' % pprint.pformat(dict_config))
#/def

class Action:
    def __init__(self, dict_config, console):
        self.dict_config = dict_config
        self.console = console
        #
        self.dict_agent = self._get_agent(constants.CFG_SECT_AGENT)
        self.dict_weblogic_admin = self._get_weblogic_admin()
        self.dict_nodemanager = self._get_nodemanager()
    #/def

    def _get_agent(self, str_name):
        str_host = self.dict_config[str_name]['host']
        int_port = self.dict_config[str_name]['port']
        str_url = "http://%s:%s" % (str_host, int_port)
        proxy = xmlrpclib.ServerProxy(str_url, allow_none=True)
        return dict(url=str_url,
                    proxy=proxy)
    #/def

    def _get_weblogic_admin(self):
        str_username = self.dict_config[constants.CFG_SECT_WEBLOGIC]['username']
        str_password = self.dict_config[constants.CFG_SECT_WEBLOGIC]['password']
        str_name = self.dict_config[constants.CFG_SECT_WEBLOGIC]['admin_server']
        str_host = self.dict_config[constants.CFG_SECT_WEBLOGIC]['admin_host']
        int_port = int(self.dict_config[constants.CFG_SECT_WEBLOGIC]['admin_port'])
        str_url = "t3://%s:%r" % (str_host, int_port)
        return dict(username=str_username,
                    password=str_password,
                    name=str_name,
                    host=str_host,
                    port=int_port,
                    url=str_url,
                    domain=self.dict_config[constants.CFG_SECT_WEBLOGIC]['domain'])
    #/def

    def _get_nodemanager(self):
        str_username = self.dict_config[constants.CFG_SECT_NODE_MANAGER]['username']
        str_password = self.dict_config[constants.CFG_SECT_NODE_MANAGER]['password']
        str_host = self.dict_config[constants.CFG_SECT_NODE_MANAGER]['host']
        int_port = int(self.dict_config[constants.CFG_SECT_NODE_MANAGER]['port'])
        return dict(username=str_username,
                    password=str_password,
                    host=str_host,
                    port=int_port)
    #/def

    def run(self, str_action, list_targets):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        #
        list_verified_targets = self._process_targets(list_targets[:])
        #
        if not list_verified_targets: return False
        #
        if str_action == 'start':
            return self._start(list_verified_targets)
        elif str_action == 'stop':
            return self._stop(list_verified_targets)
        elif str_action == 'list':
            for i in list_verified_targets:
                print i
            return True
        elif str_action == 'status':
            dict_status = self._status(list_verified_targets)
            if not dict_status:
                return False
            return self._report(dict_status, func_color=self._color_state)
        elif str_action == 'health':
            dict_health = self._health_ms(list_verified_targets)
            if not dict_health:
                return False
            return self._report(dict_health, func_color=self._color_health)
        elif str_action == 'heap':
            dict_heap = self._heap_ms(list_verified_targets)
            if not dict_heap:
                return False
            return self._report(dict_heap, func_color=self._color_heap)
        elif str_action == 'hogging':
            dict_heap = self._hogging_ms(list_verified_targets)
            if not dict_heap:
                return False
            return self._report(dict_heap, func_color=self._color_hogging)

        else:
            raise Exception("unknown action %r" % str_action) # should never reach here
        #/if
    #/def

    def _process_targets(self, list_targets):
        '''
        Verify the list to ensure that they are valid
        :param list_targets:
        :return:
        '''
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        str_weblogic_admin = self.dict_weblogic_admin["name"]
        list_servers = []
        #
        try:
            list_servers.extend(self._list_ms(bool_hide_err=True))
        except Exception:
            pinfo("unable to retrieve the server list from %r" % self.dict_weblogic_admin["name"])
        self.console.debug("list_servers=%r" % (list_servers,))
        #
        if not list_servers: # empty list (admin is probably offline)
            if str_weblogic_admin in list_targets \
                    or "all" in list_targets:
                return [str_weblogic_admin]  # if empty list, keep admin only
            return [] # list_targets = []
        #
        # list_targets not empty at this point
        if "all" in list_targets:
            list_verified_targets = list_servers[:]
            self.console.debug("list_verified_targets=%r" % (list_verified_targets[:],))
            return list_verified_targets
        #
        list_verified_targets = []
        for str_target in list_targets:
            list_match = fnmatch.filter(list_servers, str_target)
            if not list_match:
                pinfo("skipping '%s' since it's not a recognized Weblogic server" % str_target)
            for s in list_match:
                list_verified_targets.append(s)
        #/for
        list_verified_targets = sorted(list(set(list_verified_targets))) # prevent duplication (e.g. bcc list wls_*2 wls*)
        self.console.debug("list_verified_targets=%r" % (list_verified_targets,))
        return list_verified_targets
    #/def

    def _status(self, list_targets, bool_hide_err=False):
        self.console.debug("invoking %s(%r, bool_hide_err=%r)" % (inspect.stack()[0][3], list_targets, bool_hide_err))
        #
        dict_merged_status = {}
        str_admin = self.dict_weblogic_admin['name']
        list_local_targets = list_targets[:]
        #
        if str_admin in list_local_targets:
            dict_status = self._status_admin(bool_hide_err)
            if dict_status:
                list_local_targets.remove(str_admin)
                dict_merged_status.update(dict_status)
            else:
                pass # node_manager may down but we still can grab the status from wls_admin
        #/if
        #
        if list_local_targets: # still more servers to process
            dict_status = self._status_ms(list_local_targets, bool_hide_err)
            dict_merged_status.update(dict_status)
        #
        return dict_merged_status
    #/def

    def _list_ms(self, bool_hide_err=False):
        self.console.debug("invoking %s(bool_hide_err=%r)" % (inspect.stack()[0][3], bool_hide_err))
        tuple_params = (self.dict_weblogic_admin['username'],
                        self.dict_weblogic_admin['password'],
                        self.dict_weblogic_admin['url'])
        proxy = self.dict_agent['proxy']
        str_url = self.dict_agent['url']
        str_name = self.dict_weblogic_admin["name"]
        try :
            list_result = proxy.list_ms(tuple_params)
            # self.console.debug("list_result = %r" % (list_result,))
            return list_result
        except Exception, e:
            # add URL to the error message
            new_err_msg = "connecting to %r at %r:%s%s" % (str_name, str_url, type(e), e)
            self.console.debug(new_err_msg)
            if not bool_hide_err:
                perr("error connecting to %r at %r" % (str_name, str_url))
            raise Exception(new_err_msg)
        #/try
        # xmlrpclib.ProtocolError, xmlrpclib.Fault, socket.error
    #/def

    def _start(self, list_targets):
        '''
        Start logic
        :param list_targets:
        :return: (bool,
        '''
        self.console.debug("invoking %s(%r)" % (inspect.stack()[0][3], list_targets))
        # let's check wls_admin state first
        str_admin = self.dict_weblogic_admin["name"]
        dict_admin_status = self._status([str_admin])
        try:
            str_admin_state = dict_admin_status[str_admin]
        except KeyError:
            # node_manager is probably down at this point
            return
        #
        if str_admin_state == "RUNNING":
            dict_status = self._status(list_targets, bool_hide_err=True)
            #list_targets.remove(self.dict_weblogic_admin['name'])
            for str_target in list_targets[:]:
                if str_target in dict_status.keys() and \
                                dict_status[str_target] in ("RUNNING", "STARTING"):
                    pinfo("skipping '%s' since already in %s state" %
                          (str_target, self._color_state(dict_status[str_target])))
                    list_targets.remove(str_target)
            # not empty
            if not list_targets:
                self.console.debug("list is empty; nothing to do")
                #perr("list is empty; nothing to do")
                return
            return self._start_ms(list_targets)
        #
        # admin not in RUNNING state at this point
        #
        # did not request admin
        if str_admin not in list_targets:
            perr("'%s' is currently in %s state" %
                 (str_admin, self._color_state(str_admin_state)))
        #
        # admin was requested
        # only start if in SHUTDOWN STATE
        if str_admin_state not in ('SHUTDOWN', 'FORCE_SHUTTING_DOWN', 'FAILED_NOT_RESTARTABLE'):
            pinfo("please wait; '%s' is in %s state" %
                  (str_admin, self._color_state(str_admin_state)))
        list_local_targets = list_targets[:]
        list_local_targets.remove(str_admin)
        if list_local_targets:
            self._start_admin()
            return self._start_ms_offline(list_local_targets)
        return self._start_admin()
    #/def

    def _stop(self, list_targets):
        self.console.debug("invoking %s('%s')" % (inspect.stack()[0][3], list_targets))
        # let's check the wls servers' states first
        dict_admin_status = self._status([self.dict_weblogic_admin['name']], bool_hide_err=True)
        try:
            str_admin_state = dict_admin_status[self.dict_weblogic_admin['name']]
        except KeyError:
            perr("unable to connect to the node manager; is it running?")
            return
        #
        if str_admin_state != "RUNNING":
            perr("'%s' needs to be in 'RUNNING' state (currently in %s state)" %
                 (self.dict_weblogic_admin['name'], self._color_state(str_admin_state)))
            return
        #
        dict_status = self._status(list_targets, bool_hide_err=True)
        # check if already in SHUTDOWN state
        for str_target in list_targets[:]:
            str_status = dict_status.get(str_target, "UNKNOWN")
            if str_status == "SHUTDOWN":
                pinfo("skipping '%s' since already in %s state" % (str_target, self._color_state(str_status)))
                list_targets.remove(str_target)
        #/for
        # not empty
        if not list_targets:
            self.console.debug("list is empty; nothing to do")
            #perr("list is empty; nothing to do")
            return
        return self._stop_ms(list_targets)
    #/def

    def _start_admin(self):
        self.console.debug("invoking %s()" % (inspect.stack()[0][3]))
        #
        tuple_params = (self.dict_nodemanager['username'],
                        self.dict_nodemanager['password'],
                        self.dict_nodemanager['host'],
                        self.dict_nodemanager['port'],
                        self.dict_weblogic_admin['domain'],
                        self.dict_weblogic_admin['name'])
        pinfo("starting %s..." % self.dict_weblogic_admin['name'])
        try :
            self.console.debug("invoking proxy.start_wls_admin%s)" % (tuple_params,))
            self.dict_agent['proxy'].start_wls_admin(tuple_params)
            return True
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            perr("error encountered communicating with %r at %r" %
                 (gconstants.AGENT_DAEMON_NAME, self.dict_agent['url']))
        except socket.error, e:
            self.console.debug(e)
            perr("unable to connect to '%s'; is '%s' running?" %
                 (self.dict_agent['url'], gconstants.AGENT_DAEMON_NAME))
        except xmlrpclib.ProtocolError:
            return True
    #/def

    def _start_ms(self, list_targets):
        self.console.debug("invoking %s('%s')" % (inspect.stack()[0][3], list_targets))
        tuple_params = (self.dict_weblogic_admin['username'],
                        self.dict_weblogic_admin['password'],
                        self.dict_weblogic_admin['url'])
        for server in sorted(list_targets):
            pinfo("starting %s..." % server)
        try :
            return bool(self.dict_agent['proxy'].start_ms(tuple_params, list_targets))
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            perr("%s: %s" %(e.faultCode, e.faultString))
        except (xmlrpclib.ProtocolError, socket.error) as e:
            self.console.debug("%s%s" % (type(e),e))
            perr("unable to connect to '%s' at '%s'" % (gconstants.AGENT_DAEMON_NAME, self.dict_agent['url']))
    #/def

    def _start_ms_offline(self, list_targets):
        self.console.debug("invoking %s('%s')" % (inspect.stack()[0][3], list_targets))
        tuple_params = (self.dict_weblogic_admin['username'],
                        self.dict_weblogic_admin['password'],
                        self.dict_weblogic_admin['url'])
        for server in sorted(list_targets):
            pinfo("starting %s..." % server)
        try :
            return bool(self.dict_agent['proxy'].start_ms_offline(tuple_params, list_targets))
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            perr("%s: %s" %(e.faultCode, e.faultString))
        except (xmlrpclib.ProtocolError, socket.error) as e:
            self.console.debug("%s%s" % (type(e),e))
            perr("unable to connect to '%s' at '%s'" % (gconstants.AGENT_DAEMON_NAME, self.dict_agent['url']))
    #/def

    def _stop_ms(self, list_targets):
        self.console.debug("invoking %s('%s')" % (inspect.stack()[0][3], list_targets))
        tuple_params = (self.dict_weblogic_admin['username'],
                        self.dict_weblogic_admin['password'],
                        self.dict_weblogic_admin['url'])
        for server in sorted(list_targets):
            pinfo("stopping %s..." % server)
        try :
            return bool(self.dict_agent['proxy'].stop_ms(tuple_params, list_targets))
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            perr("%s: %s" %(e.faultCode, e.faultString))
        except (xmlrpclib.ProtocolError, socket.error) as e:
            self.console.debug("%s%s" % (type(e),e))
            perr("unable to connect to '%s' at '%s'" % (gconstants.AGENT_DAEMON_NAME, self.dict_agent['url']))
    #/def

    def _status_admin(self, bool_hide_err=False):
        '''
        Get the server status
        :param list_targets: list of weblogic servers status to check
        :return: dict(wls_app1=RUNNING|SHUTDOWN...)
        '''
        self.console.debug("invoking %s(bool_hide_err=%r)" % (inspect.stack()[0][3],  bool_hide_err))
        #
        tuple_params = (self.dict_nodemanager['username'],
                        self.dict_nodemanager['password'],
                        self.dict_weblogic_admin['name'],
                        self.dict_nodemanager['host'],
                        self.dict_nodemanager['port'],
                        self.dict_weblogic_admin['domain'])
        try :
            if not utils.port_listening(self.dict_nodemanager['host'],
                                        self.dict_nodemanager['port']):
                raise xmlrpclib.Fault("unable to connect",
                                      "'%s' at '%s:%s'" %
                                      (gconstants.NODE_MANAGER_NAME, # "node_manager"
                                       self.dict_nodemanager['host'],
                                       self.dict_nodemanager['port']))
            #
            self.console.debug("invoking proxy.status_admin%s" % (tuple_params,))
            dict_status = self.dict_agent['proxy'].status_admin(tuple_params)
            self.console.debug("returned '%r'" % (dict_status,))
            return dict_status
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            if not bool_hide_err:
                pinfo("%s to %s" %(e.faultCode, e.faultString))
            return dict()
        except (xmlrpclib.ProtocolError, socket.error) as e:
            self.console.debug("%s%s" % (type(e),e))
            perr("unable to connect to '%s' at '%s'" % (gconstants.AGENT_DAEMON_NAME, self.dict_agent['url']))
            sys.exit(1)
        #/try
    #/def

    def _status_ms(self, list_targets, bool_hide_err=False):
        '''
        Get the server status
        :param list_targets: list of weblogic servers to check
        :return: dict(wls_app1=RUNNING|SHUTDOWN...)
        '''
        self.console.debug("invoking %s('%s', bool_hide_err='%s')" %
                           (inspect.stack()[0][3], list_targets, bool_hide_err))
        tuple_params = (self.dict_weblogic_admin['username'],
                        self.dict_weblogic_admin['password'],
                        self.dict_weblogic_admin['url'])
        dict_status = {}
        try :
            if not utils.port_listening(self.dict_weblogic_admin['host'],
                                        self.dict_weblogic_admin['port']):
                raise xmlrpclib.Fault("unable to connect", self.dict_weblogic_admin['name'])
            dict_status = self.dict_agent['proxy'].status_ms(tuple_params, list_targets)
            self.console.debug("returned '%s'" % (dict_status,))
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            pinfo("unable to process because %r is not in 'RUNNING' state" % (self.dict_weblogic_admin['name'],))
            for server in list_targets: dict_status.setdefault(server, 'UNKNOWN')

        except (xmlrpclib.ProtocolError, socket.error) as e:
            self.console.debug("%s%s" % (type(e),e))
            perr("unable to connect to '%s' at '%s'" % (gconstants.AGENT_DAEMON_NAME, self.dict_agent['url']))
            sys.exit(1)
        #try
        return dict_status
    #/def

    def _health_ms(self, list_targets, bool_hide_err=False):
        '''
        Get the server status
        :param _health_ms: list of weblogic servers to check
        :return: dict(wls_app1=HEALTH_OK...)
        '''
        self.console.debug("invoking %s('%s', bool_hide_err='%s')" %
                           (inspect.stack()[0][3], list_targets, bool_hide_err))
        tuple_params = (self.dict_weblogic_admin['username'],
                        self.dict_weblogic_admin['password'],
                        self.dict_weblogic_admin['url'])
        dict_status = {}
        try :
            if not utils.port_listening(self.dict_weblogic_admin['host'],
                                        self.dict_weblogic_admin['port']):
                raise xmlrpclib.Fault("unable to connect", self.dict_weblogic_admin['name'])
            dict_status = self.dict_agent['proxy'].health_ms(tuple_params, list_targets)
            self.console.debug("returned '%s'" % (dict_status,))
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            pinfo("unable to process because %r is not in 'RUNNING' state" % (self.dict_weblogic_admin['name'],))
            for server in list_targets: dict_status.setdefault(server, 'UNKNOWN')
        except (xmlrpclib.ProtocolError, socket.error) as e:
            self.console.debug("%s%s" % (type(e),e))
            perr("unable to connect to '%s' at '%s'" % (gconstants.AGENT_DAEMON_NAME, self.dict_agent['url']))
            sys.exit(1)
        #try
        return dict_status
    #/def

    def _heap_ms(self, list_targets, bool_hide_err=False):
        '''
        Get the server status
        :param _healt_heap_msh_ms: list of weblogic servers to check
        :return: dict(wls_app1=865...)
        '''
        self.console.debug("invoking %s('%s', bool_hide_err='%s')" %
                           (inspect.stack()[0][3], list_targets, bool_hide_err))
        tuple_params = (self.dict_weblogic_admin['username'],
                        self.dict_weblogic_admin['password'],
                        self.dict_weblogic_admin['url'])
        dict_status = {}
        try :
            if not utils.port_listening(self.dict_weblogic_admin['host'],
                                        self.dict_weblogic_admin['port']):
                raise xmlrpclib.Fault("unable to connect", self.dict_weblogic_admin['name'])
            dict_status = self.dict_agent['proxy'].heap_ms(tuple_params, list_targets)
            self.console.debug("returned '%s'" % (dict_status,))
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            pinfo("unable to process because %r is not in 'RUNNING' state" % (self.dict_weblogic_admin['name'],))
            for server in list_targets: dict_status.setdefault(server, 'UNKNOWN')
        except (xmlrpclib.ProtocolError, socket.error) as e:
            self.console.debug("%s%s" % (type(e),e))
            perr("unable to connect to '%s' at '%s'" % (gconstants.AGENT_DAEMON_NAME, self.dict_agent['url']))
            sys.exit(1)
        #try
        return dict_status
    #/def

    def _hogging_ms(self, list_targets, bool_hide_err=False):
        '''
        Get the server status
        :param _healt_heap_msh_ms: list of weblogic servers to check
        :return: dict(wls_app1=865...)
        '''
        self.console.debug("invoking %s('%s', bool_hide_err='%s')" %
                           (inspect.stack()[0][3], list_targets, bool_hide_err))
        tuple_params = (self.dict_weblogic_admin['username'],
                        self.dict_weblogic_admin['password'],
                        self.dict_weblogic_admin['url'])
        dict_status = {}
        try :
            if not utils.port_listening(self.dict_weblogic_admin['host'],
                                        self.dict_weblogic_admin['port']):
                raise xmlrpclib.Fault("unable to connect", self.dict_weblogic_admin['name'])
            dict_status = self.dict_agent['proxy'].hogging_ms(tuple_params, list_targets)
            self.console.debug("returned '%s'" % (dict_status,))
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            pinfo("unable to process because %r is not in 'RUNNING' state" % (self.dict_weblogic_admin['name'],))
            for server in list_targets: dict_status.setdefault(server, 'UNKNOWN')
        except (xmlrpclib.ProtocolError, socket.error) as e:
            self.console.debug("%s%s" % (type(e),e))
            perr("unable to connect to '%s' at '%s'" % (gconstants.AGENT_DAEMON_NAME, self.dict_agent['url']))
            sys.exit(1)
        #try
        return dict_status
    #/def

    def _report(self, dict_status, func_color):
        self.console.debug("invoking %s('%s')" % (inspect.stack()[0][3], dict_status))
        int_maxlen = len(max(dict_status, key=len))
        if not sys.stdout.isatty(): # no interactive terminal
            int_maxlen= 0
        for server in sorted(dict_status.keys()):
            status = dict_status[server]
            print "%*s:%s" % (int_maxlen, server, func_color(status))
        #/for
        return True
    #/def

    def _color_state(self, str_status):
        if str_status == "RUNNING":
            return pgreen(str_status)
        elif str_status == "SHUTDOWN" or str_status.find("FAILED") == 0:
            return pred(str_status)
        else: # other statuses
            return pyellow(str_status)
    #/def

    def _color_health(self, str_health):
        dict_func = dict(
            HEALTH_OK=pgreen,
            HEALTH_WARN=pyellow,
            HEALTH_CRITICAL=pred,
            HEALTH_FAILED=pred,
            HEALTH_OVERLOADED=pred,
        )
        return dict_func.get(str_health, pyellow)(str_health)
        #dict_func[str_health](str_health)
    #/def

    def _color_heap(self, int_heap_usage):
        int_alarm = 95
        if int_heap_usage >= int_alarm:
            return pred(str(int_heap_usage))
        elif int_heap_usage > 0:
            return pgreen(str(int_heap_usage))
        else: # other statuses
            return pyellow(str(int_heap_usage))
    #/def

    def _color_hogging(self, int_heap_usage):
        int_alarm = 5
        if int_heap_usage >= int_alarm:
            return pred(str(int_heap_usage))
        elif int_heap_usage >= 0:
            return pgreen(str(int_heap_usage))
        else: # other statuses
            return pyellow(str(int_heap_usage))
    #/def

