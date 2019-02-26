'''
Contains aux application logic
'''

# built-in
import os
import pprint
import inspect
from os.path import expanduser
import zipfile

# custom
from lib.common import utils
from lib.common import crypto
from lib.common import log

console = log.get("console")

def config_post_processing (dict_config, **kargs):
    '''
    Post processing. Note: side-effects
    :param dict_config: dict()
    :param kargs: dict()
    :return:
    '''
    console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
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
    for str_section in dict_config.keys():
        for str_cfg in (s for s in dict_config[str_section] if s == 'password'):
            str_password = dict_config[str_section][str_cfg]
            dict_config[str_section][str_cfg] = crypto.decrypt(str_password)
    #
    console.debug('(post) dict_config=\n%s' % pprint.pformat(dict_config))
#/def

def deploy_terminfo(str_path_zip):
    console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    str_path_home = expanduser('~')
    str_path_terminfo = os.path.join(str_path_home, '.terminfo')
    if os.path.exists(str_path_terminfo):
        return True
    #/if
    if not os.path.exists(str_path_zip):
        raise IOError("%r does not exist" % str_path_zip)
    #/if
    console.debug("%r doesn't exist; let's extract %r" % (str_path_terminfo, str_path_zip))
    #
    zip_ref = zipfile.ZipFile(str_path_zip, 'r')
    zip_ref.extractall(str_path_home)
    zip_ref.close()
#/def

def set_shell_env(path_dialog_lib, str_env_term):
    console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    os.environ['TERM'] = str_env_term # http://vim.wikia.com/wiki/Getting_colors_to_work_on_solaris
    #
    if os.environ.get('LD_LIBRARY_PATH', ''):
        os.environ['LD_LIBRARY_PATH'] += ":%s" % path_dialog_lib
    else:
        os.environ['LD_LIBRARY_PATH'] = path_dialog_lib
    #/if
    console.debug("LD_LIBRARY_PATH=%r" % os.environ['LD_LIBRARY_PATH'])
#/def