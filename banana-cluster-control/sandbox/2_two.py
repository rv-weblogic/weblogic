import subprocess

def do(str_exec, list_args):
    final_cmd = [str_exec] + list_args
    print final_cmd
    subprocess.Popen(final_cmd)

str_exec = r'C:\Windows\System32\PING.EXE'
list_args = ["-n", "2", "localhost"]

do(str_exec, list_args)