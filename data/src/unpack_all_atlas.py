#! /usr/bin/python
from pathlib import Path
from unpack_atlas import main as unpack_atlas

def main(original_assets_path):
    for atlas_unpack_path in Path(original_assets_path).glob('**/*.atlas'):
        print(f'[-] Unpacking {atlas_unpack_path}')
        unpack_atlas(str(atlas_unpack_path))

if __name__ == '__main__':
    main(str(Path('./dev-resources/assets-latest')))