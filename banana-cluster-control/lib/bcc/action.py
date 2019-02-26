
# built-in
import xmlrpclib
import socket

# custom
import nm
import lib
from lib.term import *

class Action:
    def __init__(self, config, console):
        self.config = config
        self.console = console
        self.nm = nm.Nm(config, console)
        #
        # self.console.debug("Action=\n %s" % pprint.pformat(vars(self)))

    def perform(self, str_action, list_targets):
        list_unverified_targets = copy(list_targets)
        list_targets = []
        list_wls_servers = copy(self.config["internal"]["wls_servers"])

        if str_action== "status" and \
                not list_unverified_targets:
            # empty list, assume querying status on all available servers
            list_unverified_targets.append("node_manager")
            list_unverified_targets.extend(list_wls_servers)

        if "node_manager" in list_unverified_targets:
            #self.__nm__(str_action)
            self.nm.perform(str_action)
            # remove node manager from the list
            list_unverified_targets.remove("node_manager")

        for str_target in list_unverified_targets:
            if not str_target in list_wls_servers:
                pinfo("Skipping '%s' since not in the 'wls_servers' list" % str_target)
                continue
            list_targets.append(str_target)

        dict_results = dict()
        if list_targets:
            dict_results = self.__status_server__(list_targets)

        for str_server in sorted(dict_results.keys()):
            status = dict_results[str_server]
            if str_action == "start" and status != "SHUTDOWN":
                pinfo("Skipping '%s' since not in 'SHUTDOWN' state" % str_server)
                list_targets.remove(str_server)
            if str_action == "stop" and status != "RUNNING":
                pinfo("Skipping '%s' since not in 'RUNNING' state" % str_server)
                list_targets.remove(str_server)

        if list_targets: # proceed only if not empty
            if str_action == "start":
                self.console.debug("Invoking __start_server__(%s)", list_targets)
                self.__start_server__(list_targets)
            elif str_action == "stop":
                self.console.debug("Invoking __stop_server__(%s)", list_targets)
                self.__stop_server__(list_targets)
            elif str_action == "status":
                self.console.debug("Invoking __status_server__(%s)", list_targets)
                dict_results = self.__status_server__(list_targets)
                self.__status_server_report__(dict_results)

    def __start_server__(self, list_targets):
        # proxy = xmlrpclib.ServerProxy("http://localhost:35001/")
        nm_url = self.config["internal"]["bccagent_server_url"]
        self.console.debug("xmlrpclib.ServerProxy(%s)" % nm_url)
        proxy = xmlrpclib.ServerProxy(nm_url)
        for server in sorted(list_targets):
            pinfo("Starting %s..." % server)
        try :
            proxy.action_start(list_targets)

        except xmlrpclib.Fault, e:
            self.console.error("[ERROR] %s" % e)
        except socket.error:
            self.console.error("Unable to connect to '%s'. Is '%s' running?" % (nm_url, lib.SERVER_NAME))
            sys.exit(1)
        except xmlrpclib.ProtocolError:
            pass

    def __stop_server__(self, list_targets):
        # proxy = xmlrpclib.ServerProxy("http://localhost:35001/")
        wcs_url = self.config["internal"]["bccagent_server_url"]
        self.console.debug("xmlrpclib.ServerProxy(%s)" % wcs_url)
        proxy = xmlrpclib.ServerProxy(wcs_url)
        for server in sorted(list_targets):
            pinfo("Stopping %s..." % server)
        try :
            proxy.action_stop(list_targets)
        except xmlrpclib.Fault, e:
            self.console.error("[ERROR] %s" % e)
        except socket.error:
            self.console.error("Unable to connect to '%s'. Is '%s' running?" % (wcs_url, lib.SERVER_NAME))
            sys.exit(1)
        except xmlrpclib.ProtocolError:
            pass

    def __status_server__(self, list_targets):
        """
        Get the server status
        :param list_targets: list of weblogic servers to check
        :return: dict(wls_app1=RUNNING|SHUTDOWN...)
        """
        # proxy = xmlrpclib.ServerProxy("http://localhost:35001/")
        str_server_url = self.config["internal"]["bccagent_server_url"]
        self.console.debug("Invoking xmlrpclib.ServerProxy(%s) for '%s'" % (str_server_url, list_targets))
        proxy = xmlrpclib.ServerProxy(str_server_url)
        try :
            dict_results = proxy.action_status(list_targets)
            return dict_results
        except xmlrpclib.Fault, e:
            self.console.error("%s" % e)
            return dict()
        except socket.error:
            self.console.error("Unable to connect to '%s'. Is '%s' running?" % (str_server_url, lib.SERVER_NAME))
            sys.exit(1)

    def __status_server_report__(self, dict_results):
        for server in sorted(dict_results.keys()):
            status = dict_results[server]
            if status == "RUNNING":
                print "(%s) %s" % (pgreen(status), server)
            elif status == "SHUTDOWN":
                print "(%s) %s" % (pred(status), server)
            else: # other statuses
                print "(%s) %s" % (pyellow(status), server)

