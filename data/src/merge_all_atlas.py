#! /usr/bin/python
from pathlib import Path
from distutils.dir_util import copy_tree
from shutil import copyfile, rmtree
import re
import os
from common import log_normal, log_debug, log_warn, log_info, log_error
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

def main(original_assets_path, translation_path, temp_path):
    log_normal('Merge all atlas files from translation and original...', verbose)
    temp_assets_path = Path(temp_path) / 'assets'
    original_assets_path = Path(original_assets_path)
    translation_assets_path = Path(translation_path) / 'assets'

    log_info('Clean temp path...', verbose)
    if temp_assets_path.is_dir():
        rmtree(str(temp_assets_path))
    temp_assets_path.mkdir(parents=True, exist_ok=True)

    log_info('Collect atlas paths...', verbose)
    for atlas_unpack_path in sorted(original_assets_path.glob('**/*.atlas_unpack')):
        translation_atlas_path = translation_assets_path / atlas_unpack_path.relative_to(original_assets_path)
        new_atlas_path = temp_assets_path / atlas_unpack_path.relative_to(original_assets_path)
        if not translation_atlas_path.is_dir():
            continue
        log_info(f'Merge {new_atlas_path}...', verbose)
        copy_tree(str(atlas_unpack_path), str(new_atlas_path))
        for translation_sprite_path in sorted(translation_atlas_path.glob('*')):
            file_name = translation_sprite_path.name
            if file_name.endswith('.psd'):
                continue
            m = re.search(r'(\[([+-]?\d+),\s*([+-]?\d+),\s*([+-]?\d+),\s*([+-]?\d+)\])\.png$', file_name)
            if m:
                file_name = file_name.replace(m.group(1), '')

            offsetless_sprite_path = new_atlas_path / (translation_sprite_path.parent / file_name).relative_to(translation_atlas_path)
            if offsetless_sprite_path.is_file():
                offsetless_sprite_path.unlink()
                new_sprite_path = new_atlas_path / translation_sprite_path.relative_to(translation_atlas_path)
                copyfile(translation_sprite_path, new_sprite_path)
    log_info('Merge complete', verbose)

if __name__ == '__main__':
    main(
        str(Path('./assets-original')),
        str(Path('./translation')),
        str(Path('./temp'))
    )