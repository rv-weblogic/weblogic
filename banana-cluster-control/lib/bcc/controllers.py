
# built-in
import xmlrpclib, socket, sys
import inspect

# custom
from . import constants
from lib import gconstants
from lib.common.term import *
from lib.common import utils

class Action:
    def __init__(self, dict_config, console):
        self.dict_config = dict_config
        self.console = console
        #
        self.dict_agent = self.__get_agent__(constants.CFG_SECT_AGENT)
        self.dict_agent_jython = self.__get_agent__(constants.CFG_SECT_AGENT_JYTHON)
        self.dict_wls_admin = self.__get_wls_admin__()
        self.dict_node_manager = self.__get_node_manager__()

    def __get_agent__(self, str_name):
        str_address = self.dict_config[str_name]["address"]
        str_port = self.dict_config[str_name]["port"]
        str_url = "http://%s:%s" % (str_address, str_port)
        proxy = xmlrpclib.ServerProxy(str_url, allow_none=True)
        return dict(url=str_url,
                    proxy=proxy)

    def __get_wls_admin__(self):
        str_address = self.dict_config[constants.CFG_SECT_WEBLOGIC]["admin_address"]
        str_port = self.dict_config[constants.CFG_SECT_WEBLOGIC]["admin_port"]
        return dict(name=self.dict_config[constants.CFG_SECT_WEBLOGIC]["admin_server"],
                    address=str_address,
                    port=str_port,
                    url="t3://%s:%s" % (str_address, str_port),
                    host=self.dict_config[constants.CFG_SECT_WEBLOGIC]["admin_host"],
                    domain=self.dict_config[constants.CFG_SECT_WEBLOGIC]["domain"])

    def __get_node_manager__(self):
        str_address = self.dict_config[constants.CFG_SECT_NM][self.dict_wls_admin["host"]]["address"]
        str_port = self.dict_config[constants.CFG_SECT_NM][self.dict_wls_admin["host"]]["port"]
        return dict(address=str_address,
                    port=str_port)

    def run(self, str_action, list_targets):
        self.console.debug("invoking %s('%s', '%s')" % (inspect.stack()[0][3], str_action, list_targets))
        # get a list of configured ms servers
        list_ms_servers = self.dict_config[constants.CFG_SECT_WEBLOGIC]["ms_servers"][:]
        # add wls admin server to the configured list
        list_ms_servers.append(self.dict_wls_admin["name"])
        # if all is found, ignogre the rest and go with the configured list
        if "all" in list_targets:
            list_targets = list_ms_servers[:]
        #
        list_verified_targets = []
        # filter unknown targets
        for str_target in list_targets:
            if not str_target in list_ms_servers:
                pinfo("skipping '%s' since it is not in the 'ms_servers' list" % str_target)
                continue
            list_verified_targets.append(str_target)
        # no point continuing if verified list is empty
        if not list_verified_targets:
            perr("list is empty; nothing to do")
            return
        # return True if no issues found
        if str_action == "start":
            return self.__start__(list_verified_targets)
        elif str_action == "stop":
            return self.__stop__(list_verified_targets)
        elif str_action == "status":
            dict_status = self.__status__(list_verified_targets)
            if not dict_status:
                return
            return self.__status_report__(dict_status)

    def __start__(self, list_targets):
        self.console.debug("invoking %s('%s')" % (inspect.stack()[0][3], list_targets))
        # let's check wls_admin state first
        dict_admin_status = self.__status__([self.dict_wls_admin["name"]], bool_hide_err=True)
        str_admin_state = dict_admin_status[self.dict_wls_admin["name"]]
        #
        if str_admin_state == "RUNNING":
            dict_status = self.__status__(list_targets, bool_hide_err=True)
            #list_targets.remove(self.dict_wls_admin["name"])
            for str_target in list_targets[:]:
                if str_target in dict_status.keys() and \
                                dict_status[str_target] in ("RUNNING", "STARTING"):
                    pinfo("skipping '%s' since already in RUNNING or STARTING state" % str_target)
                    list_targets.remove(str_target)
            # not empty
            if not list_targets:
                perr("list is empty; nothing to do")
                return
            return self.__start_ms__(list_targets)
        #
        # not in RUNNING state at this point
        if self.dict_wls_admin["name"] in list_targets:
            # only start if in SHUTDOWN STATE
            if str_admin_state in ("SHUTDOWN", "FORCE_SHUTTING_DOWN"):
                return self.__start_admin__()
            pinfo("please wait; '%s' is neither in RUNNING nor SHUTDOWN state" % self.dict_wls_admin["name"])
        else:
            perr("'%s' needs to be in RUNNING state" % (self.dict_wls_admin["name"]))

    def __stop__(self, list_targets):
        self.console.debug("invoking %s('%s')" % (inspect.stack()[0][3], list_targets))
        # let's check the wls servers' states first
        dict_admin_status = self.__status__([self.dict_wls_admin["name"]], bool_hide_err=True)
        str_admin_state = dict_admin_status[self.dict_wls_admin["name"]]
        if str_admin_state != "RUNNING":
            perr("'%s' needs to be in RUNNING state" % (self.dict_wls_admin["name"]))
            return
        #
        dict_status = self.__status__(list_targets, bool_hide_err=True)
        # check if already in SHUTDOWN state
        for str_target in list_targets[:]:
            if str_target in dict_status.keys() and dict_status[str_target] == "SHUTDOWN":
                pinfo("skipping '%s' since already in SHUTDOWN state" % str_target)
                list_targets.remove(str_target)
        # not empty
        if not list_targets:
            perr("list is empty; nothing to do")
            return
        return self.__stop_ms__(list_targets)

    def __start_admin__(self):
        self.console.debug("invoking %s()" % (inspect.stack()[0][3]))
        #
        list_params = (self.dict_wls_admin["name"],
                       self.dict_node_manager["address"],
                       self.dict_node_manager["port"],
                       self.dict_wls_admin["domain"])
        pinfo("starting %s..." % self.dict_wls_admin["name"])
        try :
            self.console.debug("invoking proxy.start_wls_admin%s)" % (list_params,))
            #self.dict_agent_jython["proxy"].start_wls_admin(*list_params)
            self.dict_agent["proxy"].start_wls_admin(*list_params)
            return True
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            perr("unable to connect to '%s'; is it running?" % gconstants.NODE_MANAGER_NAME)
        except socket.error:
            perr("unable to connect to '%s'; is '%s' running?" %
                 (self.dict_agent_jython["url"], gconstants.AGENT_JYTHON_NAME))
            sys.exit(1)
        except xmlrpclib.ProtocolError:
            return True

    def __start_ms__(self, list_targets):
        self.console.debug("invoking %s('%s')" % (inspect.stack()[0][3], list_targets))
        for server in sorted(list_targets):
            pinfo("starting %s..." % server)
        try :
            self.dict_agent_jython["proxy"].start_ms(list_targets)
            return True
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            perr("unable to connect to '%s'; is it running?" % self.dict_wls_admin["name"])
        except socket.error:
            perr("unable to connect to '%s'; is '%s' running?" %
                 (self.dict_agent_jython["url"], gconstants.AGENT_JYTHON_NAME))
        except xmlrpclib.ProtocolError:
            return True

    def __stop_ms__(self, list_targets):
        self.console.debug("invoking %s('%s')" % (inspect.stack()[0][3], list_targets))
        for server in sorted(list_targets):
            pinfo("stopping %s..." % server)
        try :
            self.dict_agent_jython["proxy"].stop_ms(list_targets)
            return True
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            perr("unable to connect to '%s'; is it running?" % self.dict_wls_admin["name"])
        except socket.error:
            perr("unable to connect to '%s'; is '%s' running?" %
                 (self.dict_agent_jython["url"], gconstants.AGENT_JYTHON_NAME))
        except xmlrpclib.ProtocolError:
            return True

    def __status__(self, list_targets, bool_hide_err=False ):
        self.console.debug("invoking %s(%s, bool_hide_err=%s)" % (inspect.stack()[0][3], list_targets, bool_hide_err))
        #
        dict_final_status = dict()
        str_wls_admin = self.dict_wls_admin["name"]
        list_local_targets = list_targets[:]
        #
        if str_wls_admin in list_local_targets:
            dict_status = self.__status_admin__(bool_hide_err)
            list_local_targets.remove(str_wls_admin)
            dict_final_status.update(dict_status)
        #
        if list_local_targets:
            dict_status = self.__status_ms__(list_local_targets, bool_hide_err)
            dict_final_status.update(dict_status)
        #
        return dict_final_status

    def __status_admin__(self, bool_hide_err=False):
        '''
        Get the server status
        :param list_targets: list of weblogic servers to check
        :return: dict(wls_app1=RUNNING|SHUTDOWN...)
        '''
        self.console.debug("invoking %s(bool_hide_err='%s')" % (inspect.stack()[0][3],  bool_hide_err))
        list_params = (self.dict_wls_admin["name"],
                       self.dict_node_manager["address"],
                       self.dict_node_manager["port"],
                       self.dict_wls_admin["domain"])
        try :
            if not utils.ping_port(gconstants.NODE_MANAGER_NAME,
                                   self.dict_node_manager["address"],
                                   self.dict_node_manager["port"]):
                raise xmlrpclib.Fault("unable to connect",
                                      "'%s' on '%s' at '%s:%s'" %
                                      (gconstants.NODE_MANAGER_NAME,
                                       self.dict_wls_admin["host"],
                                       self.dict_node_manager["address"],
                                       self.dict_node_manager["port"]))
            self.console.debug("invoking proxy.status_admin%s" % (list_params,))
            #dict_status = self.dict_agent_jython["proxy"].status_admin(*list_params)
            # *************************
            dict_status = self.dict_agent["proxy"].status_wls_admin(*list_params)
            # *************************
            if not dict_status:
                raise xmlrpclib.Fault("unable to connect",
                                      "'%s' on '%s' at '%s:%s'" %
                                      (gconstants.NODE_MANAGER_NAME,
                                       self.dict_wls_admin["host"],
                                       self.dict_node_manager["address"],
                                       self.dict_node_manager["port"]))
            self.console.debug("returned '%r'" % (dict_status,))
            return dict_status
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            if not bool_hide_err:
                perr("%s to %s" %(e.faultCode, e.faultString))
            return dict()
        except socket.error:
            perr("unable to connect to '%s'; is '%s' running?" %
                 (self.dict_agent_jython["url"], gconstants.AGENT_JYTHON_NAME))
            sys.exit(1)

    def __status_ms__(self, list_targets, bool_hide_err=False):
        '''
        Get the server status
        :param list_targets: list of weblogic servers to check
        :return: dict(wls_app1=RUNNING|SHUTDOWN...)
        '''
        self.console.debug("invoking %s('%s', bool_hide_err='%s')" % (inspect.stack()[0][3], list_targets, bool_hide_err))
        try :
            if not utils.ping_port(self.dict_wls_admin["name"],
                                   self.dict_wls_admin["address"],
                                   self.dict_wls_admin["port"]):
                raise xmlrpclib.Fault("unable to connect", self.dict_wls_admin["name"])
            dict_status = self.dict_agent_jython["proxy"].status_ms(list_targets)
            if not dict_status:
                raise xmlrpclib.Fault("unable to connect", self.dict_wls_admin["name"])
            self.console.debug("returned '%s'" % (dict_status,))
            return dict_status
        except xmlrpclib.Fault, e:
            self.console.debug(e)
            if not bool_hide_err:
                perr("unable to connect to '%s'; is '%s' running?" %
                     (self.dict_wls_admin["url"], self.dict_wls_admin["name"]))
            return dict()
        except socket.error:
            perr("unable to connect to '%s'; is '%s' running?" %
                 (self.dict_agent_jython["url"], gconstants.AGENT_JYTHON_NAME))
            sys.exit(1)

    def __status_report__(self, dict_statuses):
        self.console.debug("invoking %s('%s')" % (inspect.stack()[0][3], dict_statuses))
        for server in sorted(dict_statuses.keys()):
            status = dict_statuses[server]
            if status == "RUNNING":
                print "(%s) %s" % (pgreen(status), server)
            elif status == "SHUTDOWN":
                print "(%s) %s" % (pred(status), server)
            else: # other statuses
                print "(%s) %s" % (pyellow(status), server)
        return True