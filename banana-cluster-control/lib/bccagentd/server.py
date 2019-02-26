# built-in
import sys
import inspect
import pprint
import xmlrpclib
import time
import subprocess

#from multiprocessing import Process
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SocketServer import ThreadingMixIn
import threading
import time

# custom
from lib.common.term import *
from lib.common import utils
from lib.common import cache
from lib.common import urlparse
from . import constants

class TimedOutException(Exception):
    pass

#
# enable multithreaded
class MultiThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass
#
class Server:
    def __init__(self, dict_config, console):
        self.dict_config = dict_config
        self.console = console
        #
        self.dict_agent_jython = self._get_agent(constants.CFG_SECT_AGENT_JYTHON)
    #/def

    def _get_agent(self, str_name):
        str_host = self.dict_config[str_name]['host']
        int_port = self.dict_config[str_name]['port']
        str_url = "http://%s:%s" % (str_host, int_port)
        proxy = xmlrpclib.ServerProxy(str_url, allow_none=True)
        return dict(url=str_url,
                    proxy=proxy)
    #/def

    def terminate(self):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    #/def

    def serve_forever(self):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        # for i in reversed(range(4)):
        #     self.console.debug("starting in %ds" % i)
        #     time.sleep(1)
        str_listen_host = self.dict_config[constants.CFG_SECT_INTERNAL]["listen_host"]
        int_listen_port = int(self.dict_config[constants.CFG_SECT_INTERNAL]["listen_port"])
        self.console.info("bccagentd is listening on 'http://%s:%s'" %(str_listen_host, int_listen_port))
        #
        server = MultiThreadedXMLRPCServer( (str_listen_host, int_listen_port), allow_none=True)
        #
        server.register_introspection_functions()
        server.register_multicall_functions()
        server.register_instance(self)
        #
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            self.console.info("terminating server")
            sys.exit(1)
    #/def

    def list_ms(self, list_params):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        #
        path_cache=self.dict_config[constants.CFG_SECT_INTERNAL]['path_cache']
        cache_expiration_sec=int(self.dict_config[constants.CFG_SECT_INTERNAL].get('cache_expiration_sec', 86400))
        #
        try:
            dict_cache = cache.load(path_cache, cache_expiration_sec)
            if not dict_cache: # valid but expired
                raise IOError # forces refresh
            #/if
            self.console.debug("returning cached data: %r" % dict_cache['data'])
            return dict_cache['data']
        except IOError:# either no cache file or expired time
            self.console.debug("%r: cache does not exist or has expired; will refresh cache" % path_cache)
            list_ms = self._get_list_ms(list_params)
            cache.save(path_cache, list_ms)
            self.console.debug("returning new data (instead from cache): %r" % list_ms)
            return list_ms
        #try
    #/def

    def _get_list_ms(self, list_params):
        try :
            list_result = self.dict_agent_jython['proxy'].list_ms(list_params)
            return list_result
        except Exception, e:
            self.console.debug(e)
            raise
        #/try
    #/def

    def status_admin(self, list_params):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        try :
            dict_result = self.dict_agent_jython['proxy'].status_admin(*list_params)
            return dict_result
        except Exception, e:
            self.console.debug(e)
            raise
    #/def

    def status_ms(self, list_params, list_targets):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        try :
            dict_result = self.dict_agent_jython['proxy'].status_ms(list_params, list_targets)
            return dict_result
        except Exception, e:
            self.console.debug(e)
            raise
    #/def

    def health_ms(self, list_params, list_targets):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        try :
            dict_result = self.dict_agent_jython['proxy'].health_ms(list_params, list_targets)
            return dict_result
        except Exception, e:
            self.console.debug(e)
            raise
    #/def

    def heap_ms(self, list_params, list_targets):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        try :
            dict_result = self.dict_agent_jython['proxy'].heap_ms(list_params, list_targets)
            return dict_result
        except Exception, e:
            self.console.debug(e)
            raise
    #/def

    def hogging_ms(self, list_params, list_targets):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        try :
            dict_result = self.dict_agent_jython['proxy'].hogging_ms(list_params, list_targets)
            return dict_result
        except Exception, e:
            self.console.debug(e)
            raise
    #/def

    def start_ms(self, list_params, list_targets):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        try :
            bool_result = self.dict_agent_jython['proxy'].start_ms(list_params, list_targets)
            return bool_result
        except Exception, e:
            self.console.debug(e)
            raise
    #/def

    def stop_ms(self, list_params, list_targets):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        try :
            bool_result = self.dict_agent_jython['proxy'].stop_ms(list_params, list_targets)
            return bool_result
        except Exception, e:
            self.console.debug(e)
            raise
    #/def

    def start_wls_admin(self, list_params):
        self.console.debug("invoking %s%r" % (inspect.stack()[0][3], list_params))
        # list_params = [ self.dict_nodemanager['username'],
        #                 self.dict_nodemanager['password'],
        #                 self.dict_nodemanager['host'],
        #                 self.dict_nodemanager['port'],
        #                 self.dict_weblogic_admin['domain'],
        #                 self.dict_weblogic_admin['name'] ]
        #
        str_path_wlst = self.dict_config[constants.CFG_SECT_AGENT_JYTHON]["path_start"]
        str_wls_admin_name = list_params.pop()
        #
        str_input = '''nmConnect%s\nnmStart(%r)\n''' % (tuple(list_params),str_wls_admin_name)
        #
        # str_input="nmConnect('soa12', 'mtogov123', '10.77.6.11', 25001, 'soa')\nnmStart('wls_admin')\n"
        #
        self.console.debug("executing '%s' with %r" % (str_path_wlst, str_input))
        dict_ret = utils.execute(list_cmd=[str_path_wlst],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.PIPE,
                                 str_input=str_input,
                                 bool_wait=False)
        return dict_ret
    #/def

    def start_ms_offline(self, list_params, list_targets, sec_sleep=3, sec_timeout=60*30):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        # list_params = connect('soa12', 'mtogov123', 't3://10.77.6.11:15001')
        try:
            t = threading.Thread(target=self._start_ms_offline,
                                 args=(list_params, list_targets, sec_sleep, sec_timeout))
            t.start()
        except Exception, e:
            self.console.debug(e)
            raise
        return True
    #/def

    def _start_ms_offline(self, list_params, list_targets, sec_sleep=3, sec_timeout=60*30):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        #
        # list_params = connect('soa12', 'mtogov123', 't3://10.77.6.11:15001')
        str_url = list_params[2]
        parse_admin = urlparse.urlparse(str_url)
        str_hostname = parse_admin.hostname
        int_port = parse_admin.port
        self.console.debug("str_url=%r, str_hostname=%r, int_port=%r" % (str_url, str_hostname,int_port))
        #
        # sec_timeout = 20
        # sec_sleep = 5
        for i in range(0, sec_timeout,  sec_sleep):
            if utils.port_listening(str_hostname, int_port):
                break
            time.sleep(sec_sleep)
        else:
            raise TimedOutException("timed out after %d sec" % sec_timeout)
        #/for
        try :
            self.dict_agent_jython['proxy'].start_ms(list_params, list_targets)
        except Exception, e:
            self.console.debug(e)
            raise
    #/def