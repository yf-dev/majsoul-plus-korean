#! /usr/bin/python
import sys
from pathlib import Path
from subprocess import Popen, PIPE

command_prefix = None
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    command_prefix = [str(Path(sys.executable).parent / 'unpack_atlas.exe')]
else:
    command_prefix = ['python', f'{str(Path(sys.argv[0]).parent / "unpack_atlas.py")}']

for atlas_unpack_path in Path("./dev-resources/assets-latest").glob('**/*.atlas'):
    print(f'[-] Packing {atlas_unpack_path}')
    p = Popen(
        command_prefix + [str(atlas_unpack_path)],
        shell=True,
        stdout=PIPE,
        stderr=PIPE
    )
    result = p.stdout.read().decode()
    result += p.stderr.read().decode()
    if result:
        print(result)