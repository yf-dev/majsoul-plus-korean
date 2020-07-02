from subprocess import Popen, PIPE

def run_cmd(cmd, print_result=True):
    p = Popen(
        cmd,
        shell=False,
        stdout=PIPE,
        stderr=PIPE
    )
    stdout, stderr = p.communicate()
    if stdout and print_result:
        print(stdout.decode())
    if stderr and print_result:
        print(stderr.decode())
    return p.returncode == 0

def order_version(a):
    return [int(i) if i.isdigit() else i for i in a.split('.')]


def log(msg, verbose_mode, is_verbose=False):
    if is_verbose and not verbose_mode:
        return
    print(msg)

def log_error(msg, verbose_mode, is_verbose=False):
    log(f'[!] {msg}', verbose_mode, is_verbose)

def log_warn(msg, verbose_mode, is_verbose=False):
    log(f'[*] {msg}', verbose_mode, is_verbose)

def log_normal(msg, verbose_mode, is_verbose=False):
    log(f'[-] {msg}', verbose_mode, is_verbose)

def log_info(msg, verbose_mode, is_verbose=False):
    log(f'[+] {msg}', verbose_mode, is_verbose)

def log_debug(msg, verbose_mode, is_verbose=True):
    log(f'[.] {msg}', verbose_mode, is_verbose)