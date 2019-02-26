'''
Contains functions related to cryptography
'''
from itertools import cycle, izip
from base64 import b64encode, b64decode

STR_PREFIX = '{XOR}'
STR_KEY = '$]z(4C36/qd}u\CJ'

def encrypt(str_txt, key=STR_KEY):
    if encrypted(str_txt):
        return str_txt
    ciphertext = ''.join(chr(ord(x) ^ ord(y)) for (x,y) in izip(str_txt, cycle(key)))
    return STR_PREFIX + b64encode(ciphertext)

def decrypt(str_txt, key=STR_KEY):
    if not encrypted(str_txt):
        return str_txt
    str_txt = str_txt[len(STR_PREFIX):]
    str_txt = b64decode(str_txt)
    return ''.join(chr(ord(x) ^ ord(y)) for (x,y) in izip(str_txt, cycle(key)))

def encrypted(str_txt):
    return str_txt.startswith(STR_PREFIX)


