#! /usr/bin/python
import os
from distutils.dir_util import copy_tree
from pathlib import Path
import os
from common import order_version, log_normal, log_debug, log_warn, log_info, log_error
lang = os.getenv('MAJSOUL_LANG', 'en')
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

lang_map = {
    'en': 2,
    'jp': 1,
}

def main(original_assets_path, cached_static_path):
    log_normal('Copy cached static data from majsoul-plus...', verbose)
    asset_path = Path(cached_static_path) / str(lang_map[lang])
    subdirs = sorted(next(os.walk(asset_path))[1], key=order_version)
    Path(original_assets_path).mkdir(parents=True, exist_ok=True)
    for subdir in subdirs:
        subdir_path = asset_path / subdir
        log_info(f'Merge {subdir_path}', verbose)
        copy_tree(str(subdir_path), original_assets_path)
    log_info('Copy complete', verbose)

if __name__ == '__main__':
    main(
        str(Path('./assets-original')),
        str(Path('../../static'))
    )