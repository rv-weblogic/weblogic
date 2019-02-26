'''
Contains functions related to configuration file parsing
'''

# built-in
import pprint, os
import ConfigParser
import inspect

# custom
from . import log

console = log.get('console')

def parse(str_file_path):
    '''
    Parse configuration file into a dictionary
    :param str_file_path: path to the configuration file
    :return: dict()
    '''
    console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    if not os.path.isfile(str_file_path):
        #console.error('file not found; unable to parse: %r' % str_file_path)
        raise IOError('configuration file %r not found' % str_file_path)
    #
    cfg = ConfigParser.ConfigParser()
    cfg.read(str_file_path)
    #
    dict_config = dict()
    for section in cfg.sections():
        dict_config.setdefault(section, {})
        for item in cfg.items(section):
            dict_config[section][item[0]] = item[1]
    #
    console.debug("dict_config=\n%s" % pprint.pformat(dict_config))
    #
    # add the path to itself
    dict_config['__self_path__'] = str_file_path
    return dict_config
