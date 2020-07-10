#! /usr/bin/python
from pathlib import Path
from unpack_atlas import main as unpack_atlas
import os
from common import log_normal, log_debug, log_warn, log_info, log_error
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

def main(original_assets_path):
    log_normal('Unpack all atlas files...', verbose)
    for atlas_unpack_path in sorted(Path(original_assets_path).glob('**/*.atlas')):
        unpack_atlas(str(atlas_unpack_path))
    log_info('Unpack complete', verbose)

if __name__ == '__main__':
    main(str(Path('./assets-original')))