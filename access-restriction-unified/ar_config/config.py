
import ConfigParser, os
import sys
import pprint

class Config:
    def __init__(self, file_path, console):
        """
        Constructor for the configuration parser
        :param exe_basename: (str) path to the exe file
        :param console: logger
        :return:
        """
        self.file_path = file_path
        self.console = console
        #
        abs_basedir = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.log_path = abs_basedir + os.sep + "logs"
        #
        self.console.debug("Config=\n{}".format(pprint.pformat(vars(self))))
        self.dict_config = self.__parse()

    def __parse(self):
        """
        Parse the config.ini file
        :param file_path: (str) full pathname of the config.ini file
        :return: dict
        """
        cfg = ConfigParser.RawConfigParser()
        if not os.path.isfile(self.file_path):
            self.console.error('File not found. Unable to parse: "{}"'.format(self.file_path) )
            #with open(self.file_path, 'w') as configfile:
            #    self.console.debug('Creating an empty file: {}'.format(self.file_path) )
        # /if
        cfg.read(self.file_path)
        dict_config = {}
        for section in cfg.sections():
            dict_config.setdefault(section, {})
            for item in cfg.items(section):
                dict_config[section][item[0]] = item[1]
        #
        self.console.debug("(pre) dict_config=\n{}".format(pprint.pformat(dict_config)))
        return self.__post_processing(dict_config)

    def __post_processing(self, dict_config):
        """
        Perform post processing (resolve special keywords such as __hostname__..etc)
        :param dict_config:
        :return: dict
        """
        # populate sections
        dict_config.setdefault("internal",dict())
        dict_config.setdefault("access_restriction",dict())
        dict_config.setdefault("email",dict())
        dict_config.setdefault("data",dict())

        dict_config["internal"].setdefault("local_admin_override", "False")
        dict_config["internal"]["local_admin_override"] = \
            self.__boolean_parser(dict_config["internal"]["local_admin_override"])

        #
        # set defaults for empty directives
        dict_config["internal"].setdefault("appcmd", r"c:\windows\system32\inetsrv\appcmd.exe")
        dict_config["internal"].setdefault("log_directory", "logs")
        dict_config["internal"].setdefault("log_fmt", "%Y%m%d_%H%M%S_%f.log")
        dict_config["internal"].setdefault("notepad", r"c:\windows\system32\notepad.exe")

        for key in ["ips", "ar_url"]:
            dict_config["access_restriction"].setdefault(key, "")

        for key in "relay_server_port,recipients," \
                   "relay_server_host,ar_disabled_subject," \
                   "ar_disabled_body,ar_enabled_subject," \
                   "ar_enabled_body,email_from," \
                   "email_notification".split(","):
            dict_config["email"].setdefault(key, "")
        dict_config["email"]["email_notification"] = self.__boolean_parser(dict_config["email"]["email_notification"])

        dict_config["data"].setdefault("saved_list","")

        self.console.debug("(post) dict_config=\n{}".format(pprint.pformat(dict_config)))
        return dict_config

    def __boolean_parser(self, input):
        if input.lower() == "true":
            return True
        return False
