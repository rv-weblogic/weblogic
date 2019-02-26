# built-in
import time
import pickle
import copy
import inspect
import pprint
import log

console = log.get('console')

def save(str_path, data):
    console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    _save_cache(str_path, data)

def load(str_path, sec_expired=86400):
    console.debug("invoking %s(%s)" % (inspect.stack()[0][3], pprint.pformat(locals())))
    obj = _load_cache(str_path)
    time_now = time.time()
    time_obj = obj.get('time', 0)
    if not time_obj:
        console.debug("could not retrieve time from cached object")
        return None
    #/if
    time_since = time_now - time_obj
    if time_since > sec_expired:
        console.debug("cache expired; %.2f - %.2f = %.2fsec is greater than %.2fsec" %
                      (time_now, time_obj, time_since, sec_expired))
        return None
    #/if
    console.debug("successfully retrieved cached object: %r" % obj)
    return obj

def _save_cache(str_path, data):
    obj_cache = dict(time=time.time(), data=copy.deepcopy(data))
    f = open(str_path, 'wb')
    pickle.dump(obj_cache, f)
    f.close()

def _load_cache(str_path):
    f = open(str_path, 'rb')
    obj = pickle.load(f)
    f.close()
    return obj