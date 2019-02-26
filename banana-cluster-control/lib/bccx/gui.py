
# built-in
import os
import inspect
import pprint
import subprocess
import time
import sys
import datetime

# custom
from . import constants
from lib.common import utils
from lib.common.term import *

class GUI:
    def __init__(self, dict_config, console):
        self.dict_config = dict_config
        self.console = console
    #/def

    def run(self, str_action, list_targets):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        str_action = str_action.lower()
        bool_direct_entry = True if str_action else False
        while True:
            str_action = str_action.lower()
            if str_action in ('start', 'stop'):
                try:
                    self._selection(list_targets, str_action.capitalize())
                except KeyboardInterrupt:
                    pass
                #/try
                if bool_direct_entry: return
                str_action = ''
            elif str_action in ('status', 'health', 'heap', 'hogging'):
                try:
                    self._get_stats(list_targets, str_action)
                except KeyboardInterrupt:
                    pass
                #/try
                if bool_direct_entry: return
                str_action = ''
            elif str_action in ('deploy', 'schedule', 'hogging'):
                self._not_implemented()
                str_action = ''
            elif str_action == 'exit':
                return
            else:
                str_action = self._menu()
                bool_direct_entry = False
            #/if
        #/while
    #/def

    def _not_implemented(self):
        self._msgbox(str_msg="This feature has not been implemented.", height=5, width=45)
    #/def

    def _get_list(self, list_targets):
        '''
        Get the server list
        :param list_targets: list (may contain glob)
        :return: list
        '''
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        if not list_targets:
            list_targets = ['all']
        dict_return = self._call(list_targets, 'list')
        if '[ERROR]' in dict_return['stderr']:
            raise Exception(dict_return['stderr'])
        #/if
        list_servers = dict_return['stdout'].strip().split()
        return list_servers
    #/def

    def _call(self, list_targets, str_action):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        list_cmd = [self.dict_config['path_bcc'], str_action]
        list_cmd.extend(list_targets)
        dict_return = utils.execute(list_cmd,
                                    stdout=subprocess.PIPE, # prevent colour getting added
                                    stderr=subprocess.PIPE,
                                    bool_comm=True,
                                    )
        return dict_return
    #/def

    def _get_output(self, list_targets, str_action):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        if not str_action:
            # expecting ('status', 'health', 'heap', 'hogging')
            raise Exception("no action requested")
        #/if
        if not list_targets:
            list_targets = ['all']
        #
        dict_return = self._call(list_targets, str_action)
        #
        if '[ERROR]' in dict_return['stderr']:
            raise Exception(dict_return['stderr'])
        #/if
        list_result = dict_return['stdout'].strip().split()
        list_result_split = [i.split(':') for i in list_result]
        #
        dict_value = dict()
        for k,v in list_result_split:
            dict_value.setdefault(k,v)
        #/for
        return dict_value
    #/def

    def _menu(self):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        dict_return = utils.execute([self.dict_config['path_dialog'], '--backtitle', '%s v%.2f' %
                                     (constants.FRIENDLY_FULLNAME, constants.VERSION),
                                     '--no-cancel', '--menu', ' ', '0', '0', '0',
                                     'Start', 'Start Weblogic application servers',
                                     'Stop', 'Stop Weblogic application servers',
                                     'Status', 'Check the status of Weblogic application servers',
                                     'Deploy', 'Deploy a Weblogic application',
                                     'Schedule', 'Schedule a task',
                                     'Health', 'Perform health check',
                                     'Heap', 'Monitor JVM heap usage',
                                     'Hogging', 'Monitor JVM hung threads',
                                     'Exit', 'Exit out of this menu'
                                    ],
                                    stderr=subprocess.PIPE,
                                    bool_comm=True,
                                    bool_signal_propagation=True,
                                    )
        str_choice = dict_return['stderr'].lower()
        return str_choice
    #/def

    def _selection(self, list_targets, str_action='OK'):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        self._show_loading()
        # check for WLS runtime state (e.g. RUNNING, SHUTDOWN..etc)
        try:
            dict_status = self._get_output(list_targets, str_action='status')
            if not dict_status:
                raise Exception('No match for %r' % list_targets)
        except Exception, e:
            self._msgbox(str_msg='An error has occurred. Select "Show Error" for more information.', str_err=str(e))
            return
        #/try
        #
        list_cmd = [self.dict_config['path_dialog'], '--colors', '--backtitle', '%s v%.2f' %
                    (constants.FRIENDLY_FULLNAME, constants.VERSION),
                    '--ok-label', str_action, '--stderr', '--checklist', '%s:' % str_action,'0', '0', '0']
        #
        list_servers = []
        for server in sorted(dict_status):
            status = dict_status[server]
            list_servers.append(server)
            if str_action.lower() == 'stop':
                if status in ('RUNNING'):
                    list_servers.extend([status, 'on'])
                else:
                    list_servers.extend([status, 'off'])
                #/if
            elif str_action.lower() == 'start':
                if status in ('SHUTDOWN', 'FORCE_SHUTTING_DOWN', 'FAILED_NOT_RESTARTABLE'):
                    list_servers.extend([status, 'on'])
                else:
                    list_servers.extend([status, 'off'])
                #/if
            #/if
        #/for
        list_cmd.extend(list_servers)
        self.console.debug(pprint.pformat(list_cmd))
        dict_return = utils.execute(list_cmd,
                                    stderr=subprocess.PIPE,
                                    bool_comm=True,
                                    bool_signal_propagation=True,
                                    )
        if not dict_return['stderr']:
            self._msgbox(str_msg='No items selected.', height=5, width=30)
            return
        list_selected = dict_return['stderr'].strip().split()
        dict_return = self._call(list_selected, str_action)
        str_output = dict_return['stderr'] # not expecting anything from stdout
        self._msgbox(str_msg=str_output)
    #/def

    def _show_loading(self):
        list_cmd = [self.dict_config['path_dialog'], '--progressbox', 'loading...', '0', '0']
        dict_return = utils.execute(list_cmd,
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE,
                                    bool_comm=True,
                                    bool_signal_propagation=True,)
        loading_screen = dict_return['stdout']
        sys.stdout.write(loading_screen)
    #/def

    def _msgbox(self, str_msg='', str_err='', height=0, width=0, ok_label='OK'):
        while True:
            list_cmd = [self.dict_config['path_dialog'], '--colors', '--backtitle', '%s v%.2f' %
                        (constants.FRIENDLY_FULLNAME, constants.VERSION),
                        '--ok-label', ok_label, '--stderr',
                        '--msgbox', str_msg, str(height), str(width)]
            if str_err:
                list_cmd[1:1] = ['--help-button', '--help-label', 'Show Error']
            dict_return = utils.execute(list_cmd,
                                        bool_comm=True,
                                        bool_signal_propagation=True)
            if dict_return['ret'] == 2:
                self._debugbox(str_err)
            else:
                break
            #/if
        #while
    #/def

    def _debugbox(self, str_msg='', height='0', width='0'):
        self._msgbox(str_msg, '', height, width)
    #/def

    def _get_stats(self, list_targets, str_action):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        self._show_loading()
        while True:
            try:
                list_targets = self._get_list(list_targets)
                dict_stats = self._get_output(list_targets, str_action=str_action)
                # no need to check if dict_details is empty since _get_output will automatically assume 'all'
            except Exception, e:
                self._msgbox(str_msg='An error has occurred. Select "Show Error" for more information.', str_err=str(e))
                return
            #/try
            str_pct = str(self._gauge(dict_stats, str_action))
            dict_status_colored = self._colorize(dict_stats, str_action)
            #
            now = datetime.datetime.today() #now().strftime('%H:%M:%S:%f')
            list_cmd = [self.dict_config['path_dialog'], '--colors', '--backtitle', '%s v%.2f (last updated on %s)' %
                        (constants.FRIENDLY_FULLNAME, constants.VERSION, now)]
            list_cmd.extend(['--mixedgauge', 'Press Ctrl-c to exit.', '0', '30', str_pct])
            #
            for server in sorted(dict_status_colored):
                status = dict_status_colored[server]['status']
                # '-1'.isdigit == False so let's strip the negative symbol
                # https://stackoverflow.com/questions/28279732/how-to-type-negative-number-with-isdigit
                if status.lstrip('-').isdigit():
                    if str_action == 'heap':
                        status = '-%s' % status
                    else:
                        status = '=> %s' %status
                    #/if
                #/if
                server_colorized = dict_status_colored[server]['colorized']
                list_cmd.extend([server_colorized, status])
            #/for
            utils.execute(list_cmd,
                          bool_comm=True,
                          bool_signal_propagation=True)
            time.sleep(self.dict_config['refresh_rate_sec'])
        #/while
    #/def

    def _gauge(self, dict_stats, str_action):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        if not dict_stats:
            raise ValueError("dict_stats is empty")
        #/if
        dict_ok = dict(status='RUNNING',
                       health='HEALTH_OK',
                       heap=self.dict_config['limit_heap_usage'],
                       hogging=self.dict_config['limit_hogging_thread'])
        ok = dict_ok[str_action]
        int_pct = 0
        if type(ok) == str:
            # string
            running_count = float(len([k for k, v in dict_stats.iteritems() if v == ok]))
        else:
            # number
            running_count = float(len([k for k, v in dict_stats.iteritems() if int(v) >=0 and int(v) <= ok]))
        #/if
        int_total = len(dict_stats)
        self.console.debug("running_count=%r" % running_count)
        int_pct = int(round( (running_count/int_total) * 100 ))
        return int_pct
    #/def

    def _colorize(self, dict_stats, str_action, int_trim_limit=10):
        self.console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
        if not dict_stats:
            raise ValueError("dict_stats is empty")
        #/if
        #
        dict_ref = dict(
            on=('RUNNING', 'HEALTH_OK'),
            off=('SHUTDOWN', 'FAILED'))
        dict_status_colored = {}
        for server in dict_stats:
            status = dict_stats[server]
            status_trimmed = status[:int_trim_limit]
            if status.isdigit():
                if str_action == 'heap':
                    int_heap_usage = int(status)
                    int_alarm = self.dict_config['limit_heap_usage']
                    # red(1), green(2), yellow(3)
                    if int_heap_usage >= int_alarm:
                        server_colorized = '\Z1%s\Zn' % server
                    elif int_heap_usage > 0:
                        server_colorized = '\Z2%s\Zn' % server
                    else: # other statuses
                        server_colorized = '\Z3%s\Zn' % server
                    #/if
                elif str_action == 'hogging':
                    int_heap_usage = int(status)
                    int_alarm = self.dict_config['limit_hogging_thread']
                    # red(1), green(2), yellow(3)
                    if int_heap_usage >= int_alarm:
                        server_colorized = '\Z1%s\Zn' % server
                    elif int_heap_usage >= 0:
                        server_colorized = '\Z2%s\Zn' % server
                    else: # other statuses
                        server_colorized = '\Z3%s\Zn' % server
                    #/if
                #/if
            else:
                #
                if [m for m in dict_ref['on'] if m in status]: #status == 'RUNNING':
                    server_colorized = '\Z2%s\Zn' % server #green
                elif [m for m in dict_ref['off'] if m in status]: #status == 'SHUTDOWN' or 'FAILED' in status:
                    server_colorized = '\Z1%s\Zn' % server #red
                else:
                    server_colorized = '\Z3%s\Zn' % server #yellow
                #/if
            #/if
            dict_status_colored.setdefault(server, {})
            dict_status_colored[server].setdefault('status', status_trimmed)
            dict_status_colored[server].setdefault('colorized', server_colorized)
        #/for
        return dict_status_colored
    #/def

