#! /usr/bin/python
import os
from distutils.dir_util import copy_tree
from pathlib import Path
import os
lang = os.getenv('MAJSOUL_LANG', 'en')

lang_map = {
    'en': 2,
    'jp': 1,
}

def order_version(a):
    return [int(i) if i.isdigit() else i for i in a.split('.')]

def main(original_assets_path, cached_static_path):
    asset_path = Path(cached_static_path) / lang_map[lang]
    subdirs = sorted(next(os.walk(asset_path))[1], key=order_version)
    Path(original_assets_path).mkdir(parents=True, exist_ok=True)
    for subdir in subdirs:
        subdir_path = f'{asset_path}/{subdir}'
        print(f'Merging {subdir_path}')
        copy_tree(f'{asset_path}/{subdir}', original_assets_path)

if __name__ == '__main__':
    main(
        str(Path('./dev-resources/assets-latest')),
        str(Path('../../static'))
    )