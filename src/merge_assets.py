#! /usr/bin/python
import os
import shutil
from distutils.dir_util import copy_tree
from pathlib import Path
import os
lang = os.getenv('MAJSOUL_LANG', 'en')

lang_map = {
    'en': 2,
    'jp': 1,
}

ASSET_PATH = f'../../static/{lang_map[lang]}'
TARGET = './dev-resources/assets-latest'

def order_version(a):
    return [int(i) if i.isdigit() else i for i in a.split('.')]

subdirs = sorted(next(os.walk(ASSET_PATH))[1], key=order_version)
shutil.rmtree(TARGET, ignore_errors=True)
Path(TARGET).mkdir(parents=True, exist_ok=True)
for subdir in subdirs:
    subdir_path = f'{ASSET_PATH}/{subdir}'
    print(f'Merging {subdir_path}')
    copy_tree(f'{ASSET_PATH}/{subdir}', TARGET)

