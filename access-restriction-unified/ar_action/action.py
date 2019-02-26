
from subprocess import PIPE
import subprocess
import os, sys
import re
from datetime import datetime

from collections import OrderedDict
from pprint import pprint, pformat
from ar_mail import mail

import getpass, platform

import ConfigParser

import ar_log.log as ar_log
console = ar_log.get_logger("console")

class Action:
    def __init__(self, config, console=console):
        '''
        Any action related codes go here (MVC)
        :param config: (dict) configuration
        :return: None
        '''
        self.config = config
        self.console = console
        self.appcmd = self.config.dict_config["internal"]["appcmd"]

    def execute(self, exe, list_args, stdin="", invisible=True, block=True):
        """
        Execute external command
        :param exe: (str) the full path to the exe file
        :param list_args: (list) list of parameters to be included
        :param stdin:
        :param invisible: (boolean) hide the command
        :param block: (boolean) block the main application while waiting?
        :return: None
        """
        startupinfo = None
        result = dict()

        if os.name == 'nt' and invisible:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        for key in ["stdout", "stderr"]:
            result[key] = ""
        result["retcode"] = 1

        try:
            list_cmd = [exe] + list_args
            console.debug("Executing:\n{}".format(list_cmd))
            cmd = subprocess.Popen(list_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, startupinfo=startupinfo)

            if block:
                result["stdout"], result["stderr"]= cmd.communicate(stdin)
                result["stdout"] = result["stdout"].strip()
                result["stderr"] = result["stderr"].strip()
                result["retcode"] = cmd.returncode
        except WindowsError:
            console.error("Cannot find executable file: '{}'".format(exe))
            console.error("Failed to execute: '{}'".format(list_cmd))
        #
        return result

    def get_websites(self):
        """
        Get the dict_websites from appcmd
        :param: None
        :return: (OrderDict) list of dict_websites and their child dict_websites
        """
        result = self.execute(self.appcmd, ["list", "apps", "-text:app.name"])
        data = result["stdout"]

        if not result["retcode"] == 0 or not data:
            return [], OrderedDict() # return empty dict if something goes wrong

        list_websites = re.split("\r\n", data)

        dict_websites = OrderedDict()
        for line in list_websites:
            separated = line.split("/")
            parent = separated[0]
            child = "/" + separated[1] # "root" will show up as "/"
            if dict_websites.has_key(parent):
                dict_websites[parent].append(child)
            else:
                dict_websites.setdefault(parent, [child])
        return list_websites, dict_websites

    def change_state(self, action, websites):
        """
        Change the AR state
        :param action: (str) enable/disable
        :param websites: (list) list of websites to be performed on
        :return: (str) output of the run
        """
        result = dict()

        ips = self.config.dict_config["access_restriction"]["ips"].split("\n")
        ooo_url = self.config.dict_config["access_restriction"]["ar_url"]

        console.debug("Change AR state on websites:\n{}\n"
                      "ooo_url:{}\n".
                      format(websites, ooo_url,))
        for website in websites:
            if action == "enable":
                result[website] = self.__enable_ar(website, ooo_url, ips)
            elif action == "disable":
                result[website] = self.__disable_ar(website, ooo_url, ips)
            console.debug(pformat(result))

        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        output = "=" * 80
        if action == "enable":
            output += "\n[{} {}] Enabling Access Restriction...\n\n".format(date, getpass.getuser().lower())
        elif action == "disable":
            output += "\n[{} {}] Disabling Access Restriction...\n\n".format(date, getpass.getuser().lower())
        for website in websites:
            failed_flag = False
            for section in result[website]:
                retcode = result[website][section]["retcode"]
                if retcode != 0:
                    failed_flag = True
            if not failed_flag:
                output += "[OK] {website}\n".format(website=website)

            else:
                output += "[ERROR] {website}\n".format(website=website)
                for section in result[website]:
                    retcode = result[website][section]["retcode"]
                    stdout = result[website][section]["stdout"]

                    status = "OK"
                    if retcode != 0:
                        status = "ERROR"

                    output += "\t[{status}] {section} - (retcode={retcode})\n".format(
                        status=status, section=section, retcode=retcode)
                    if retcode != 0:
                        output += "\t > {}\n".format(stdout)
            # /else
        # /for website in result:
        output += "\n"
        output += "=" * 80
        return output

    def write_log(self, output):
        """
        Log writing helper
        :param output: data to be written
        :return: (str) the full path to the log file
        """
        str_abs_basedir = os.path.dirname(os.path.realpath(sys.argv[0]))
        str_logpath =  os.path.join(str_abs_basedir,
                                     self.config.dict_config["internal"]["log_directory"])
        str_logfile = os.path.join(str_logpath,
                                    datetime.strftime(datetime.now(), self.config.dict_config["internal"]["log_fmt"]))
        #
        if not os.path.isdir(str_logpath):
            console.debug('Log directory not found. Attempting to create it.')
            os.mkdir(str_logpath)
        #
        with open(str_logfile, 'a') as logfile:
            console.debug('Writing output to: {}'.format(str_logfile))
            logfile.write(output)
        return str_logfile

    def __enable_ar(self, website, ooo_url, ips):
        """
        Enable access restriction
        :param websites: (list) list of websites to be performed on
        :param ooo_url: (str) ooo website
        :param ips: (list) exempted ips
        :return: (dict) result of the run
        """
        result = OrderedDict()
        #####################
        # ipSecurity-base
        #####################
        cmd = self.execute(self.appcmd, ["set", "config", website,
                                            "-section:system.webServer/security/ipSecurity",
                                            "-allowUnlisted:false",
                                            "-commit:apphost"
                                            ])
        result["ipSecurity-base"] = dict.copy(cmd)
        #
        #####################
        # ipSecurity-<0..x>
        #####################
        for ip in ips:
            cmd = self.execute(self.appcmd, ["set", "config", website,
                                                "-section:system.webServer/security/ipSecurity",
                                                "-+[ipAddress='%s',allowed='true']" % ip,
                                                "-commit:apphost"])
            result["ipSecurity-{}".format(ip)] = dict.copy(cmd)
        #
        #####################
        # httpErrors-403.6
        #####################
        cmd = self.execute(self.appcmd, ["set", "config", website,
                                         "-section:system.webServer/httpErrors",
                                         "--[statusCode='403', subStatusCode='6']",
                                         "-commit:url"])
        result["httpErrors-403.6"] = dict.copy(cmd)
        result["httpErrors-403.6"]["retcode"] = 0
        #
        #####################
        # httpErrors-403
        #####################
        cmd = self.execute(self.appcmd, ["set", "config", website,
                                         "-section:system.webServer/httpErrors",
                                         "--[statusCode='403']",
                                         "-commit:url"])
        result["httpErrors-403"] = dict.copy(cmd)
        result["httpErrors-403"]["retcode"] = 0
        #
        #####################
        # httpErrors+403
        #####################
        cmd = self.execute(self.appcmd, ["set", "config", website,
                                         "-section:system.webServer/httpErrors",
                                         #"-+[statusCode='403',subStatusCode='6',prefixLanguageFilePath='',path='%s',responseMode='Redirect']" % ooo_url,
                                         "-+[statusCode='403',prefixLanguageFilePath='',path='%s',responseMode='Redirect']" % ooo_url,
                                         "-commit:url"])
        result["httpErrors+403"] = dict.copy(cmd)
        return result

    def __disable_ar(self, website, ooo_url, ips):
        """
        Disable access restriction
        :param websites: (list) list of websites to be performed on
        :param ooo_url: (str) ooo website
        :param ips: (list) exempted ips
        :return: (dict) result of the run
        """
        result = OrderedDict()
        #####################
        # ipSecurity-base
        #####################
        cmd = self.execute(self.appcmd, ["clear", "config", website,
                                            "-section:system.webServer/security/ipSecurity",
                                            "-commit:apphost"
                                            ])
        result["ipSecurity-base"] = dict.copy(cmd)
        #
        #####################
        # httpErrors-base
        #####################
        # cmd = self.execute(self.appcmd, ["clear", "config", website,
        #                                  "-section:system.webServer/httpErrors",
        #                                  "-commit:app"])
        # result["httpErrors-base"] = dict.copy(cmd)

        #####################
        # httpErrors+403
        #####################
        cmd = self.execute(self.appcmd, ["set", "config", website,
                                         "-section:system.webServer/httpErrors",
                                         #"-+[statusCode='403',subStatusCode='6',prefixLanguageFilePath='',path='%s',responseMode='Redirect']" % ooo_url,
                                         "--[statusCode='403',prefixLanguageFilePath='',path='%s',responseMode='Redirect']" % ooo_url,
                                         "-commit:url"])
        result["httpErrors-403"] = dict.copy(cmd)
        return result

        return result

    def send_email(self, ar_state, websites):
        """
        Send the notification email
        :param ar_state: (str) ar_enabled/ar_disabled
        :param websites: (list) list of websites to be included in the email body
        :return: (str) error if any
        """
        email_from = self.config.dict_config["email"]["email_from"]
        _username_ = getpass.getuser().lower()
        _hostname_ = platform.node().lower()
        #
        try:
            email_from = email_from.format(_username_=_username_,
                                           _hostname_=_hostname_)
        except KeyError:
            _type, e, _trace = sys.exc_info()
            self.console.debug(e)
            pass

        email_to = self.config.dict_config["email"]["recipients"].split("\n")
        subject_content = self.config.dict_config["email"][ar_state+"_subject"]
        #
        try:
            subject_content = subject_content.format(_hostname_=_hostname_)
        except KeyError:
            pass

        body_content = self.config.dict_config["email"][ar_state+"_body"]
        _websites_ = "\n".join(list(websites))

        try:
            body_content = body_content.format(_websites_=_websites_)
        except KeyError:
            pass

        relay_server_host = self.config.dict_config["email"]["relay_server_host"]
        relay_server_port = self.config.dict_config["email"]["relay_server_port"]

        err = mail.send(email_from = email_from,
                        email_to = email_to,
                        email_subject = subject_content,
                        email_body = body_content,
                        server_host = relay_server_host,
                        server_port = relay_server_port
        )
        console.debug("Email result: {}".format(err))
        return err

    def save_config(self):
        new_config = ConfigParser.RawConfigParser()
        # sync self.conf.dict_config to the new config file
        for section in self.config.dict_config:
            new_config.add_section(section)
            for item in self.config.dict_config[section]:
                new_config.set(section, item, self.config.dict_config[section][item])
        #
        # saving to a file
        with open(self.config.file_path, 'w') as newconfigfile:
            new_config.write(newconfigfile)
        #
        self.console.debug("Configuration has been saved to '%s'" % self.config.file_path)