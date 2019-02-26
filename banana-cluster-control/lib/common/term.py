'''
Contains functions related to terminal/shell printing
'''

# built-in
import sys
import string

RED = "\033[1;41m"
GREEN = "\033[1;42m"
YELLOW = "\033[1;43m"
BLUE = "\033[1;44m"
MAGENTA = "\033[1;45m"
CYAN = "\033[1;46m"
NORMAL = "\033[0m"

# sigh.. this will probably make baby Jesus cry but I'm too lazy to empty out these constants
# detect if not terminal then don't add colour!
for colour in locals().copy(): # this is because locals() tend to dynamically change
    if not sys.stdout.isatty() and \
                    colour[0] in string.ascii_uppercase[:26]:
        # e.g. RED = "", GREEN = "" ...
        locals()[colour] = ""

def pred(str):     return RED + str + NORMAL
def pgreen(str):   return GREEN + str + NORMAL
def pyellow(str):  return YELLOW + str + NORMAL
def pblue(str):    return BLUE + str + NORMAL
def pmagenta(str): return MAGENTA + str + NORMAL
def pcyan(str):    return CYAN + str + NORMAL

def pinfo(str, newline=True):
    str_postfix = ""
    if newline: str_postfix += "\n"
    sys.stderr.write("[%s] %s%s" % (pblue("INFO"), str, str_postfix))

def perr(str, newline=True):
    str_postfix = ""
    if newline: str_postfix += "\n"
    sys.stderr.write("[%s] %s %s" % (pred("ERROR"), str, str_postfix))
