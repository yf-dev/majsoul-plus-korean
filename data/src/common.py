from subprocess import Popen, PIPE

def run_cmd(cmd, print_result=True):
    print(f'[-] Run command: {" ".join(cmd)}')
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