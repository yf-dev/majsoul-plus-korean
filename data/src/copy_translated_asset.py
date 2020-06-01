#! /usr/bin/python
import os
from pathlib import Path
from shutil import copyfile
lang = os.getenv('MAJSOUL_LANG', 'en')

def main(translation_path, dist_path):
    for file_path in sorted((Path(translation_path) / 'assets').glob('**/*')):
        if file_path.is_dir():
            continue
        if '.atlas_unpack' in str(file_path):
            continue
        if file_path.name.endswith('.psd'):
            continue

        dest_path = Path(dist_path) / file_path.relative_to(Path(translation_path))
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        print(f'[+] Copy file: {file_path}')
        copyfile(str(file_path), str(dest_path))
if __name__ == '__main__':
    main(
        str(Path('./translation')),
        str(Path('..'))
    )