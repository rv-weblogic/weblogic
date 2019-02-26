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
    for str_section in (constants.CFG_SECT_INTERNAL, ):
        #for str_cfg in ('path_start', 'path_ini', 'path_log', 'path_pid'):
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

def add_opts(parser):
    # add nonblock mode
    parser.add_option('-n', '--nonblock', help='enable non-blocking mode (useful for scripting)',
                      action='store_const', const=False,
                      default=True, dest='block')
    # add force mode
    parser.add_option('-f', '--force', help='use SIGKILL[9] for stop instead of SIGTERM[15]',
                      action='store_const',
                      default=-1, dest='timeout')
    # add timeout override
    parser.add_option('-t', '--timeout', help='override the timeout value in the config file',
                      metavar='sec', type='int',
                      dest='timeout')
    opt, argv = parser.parse_args()
    return parser, opt, argv
