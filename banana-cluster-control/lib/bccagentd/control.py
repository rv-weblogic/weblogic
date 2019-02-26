'''
Contains aux application logic
'''

# built-in
import pprint
import os

# custom
from . import constants
from lib.common import log
from lib.common import utils

console = log.get('console')

def config_post_processing (dict_config, **kargs):
    '''
    Post processing. Note: side-effects
    :param dict_config: dict()
    :param kargs: dict()
    :return:
    '''
    str_abs_rootdir = kargs['str_abs_rootdir'] # /dir
    #
    for str_section in dict_config.keys():
        for str_cfg in (s for s in dict_config[str_section] if s.startswith("path_")):
            try :
                str_rel_path = dict_config[str_section][str_cfg]
            except KeyError:
                continue # skip empty str_cfg
            str_full_path = os.path.join(str_abs_rootdir, str_rel_path)
            utils.ensure_dir(str_full_path)
            dict_config[str_section][str_cfg] = str_full_path
    #
    console.debug('(post) dict_config=\n%s' % pprint.pformat(dict_config))
#/def
