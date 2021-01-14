import os
from subprocess import Popen, PIPE

AVAILABLE_LANGS = {"chs": "zh-CN", "chs_t": "zh-TW", "jp": "jp", "en": "en"}

mpk_lang = os.getenv("MAJSOUL_LANG", "en")
mpk_verbose = int(os.getenv("MAJSOUL_VERBOSE", "0")) == 1
mpk_resourcepack_id = os.getenv("MAJSOUL_RESOURCEPACK_ID", "korean")
mpk_resourcepack_name = os.getenv("MAJSOUL_RESOURCEPACK_NAME", "한국어(글로벌 서버)")


def run_cmd(cmd, print_result=True):
    process = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    if stdout and print_result:
        print(stdout.decode())
    if stderr and print_result:
        print(stderr.decode())
    return process.returncode == 0


def order_version(version_string):
    """
    Convert version string to list of int for comparing or sorting
    """
    return [int(i) if i.isdigit() else i for i in version_string.split(".")]


def log(msg, is_verbose=False):
    if is_verbose and not mpk_verbose:
        return
    print(msg)


def log_error(msg, is_verbose=False):
    log(f"[!] {msg}", is_verbose)


def log_warn(msg, is_verbose=False):
    log(f"[*] {msg}", is_verbose)


def log_normal(msg, is_verbose=False):
    log(f"[-] {msg}", is_verbose)


def log_info(msg, is_verbose=False):
    log(f"[+] {msg}", is_verbose)


def log_debug(msg, is_verbose=True):
    log(f"[.] {msg}", is_verbose)
