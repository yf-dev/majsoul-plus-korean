#! /usr/bin/python
import os
import shutil
from distutils.dir_util import copy_tree
from pathlib import Path

ASSET_PATH = '../../static/2'
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

