#! /usr/bin/python
from PIL import Image
import json
import os
import sys
from pathlib import Path
import os
from common import log_normal, log_debug, log_warn, log_info, log_error

verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

def main(atlas_path):
    log_normal(f'Unpack {atlas_path}...', verbose)
    atlas = None

    atlas_path = Path(atlas_path)

    log_info('Read atlas...', verbose, is_verbose=True)
    with atlas_path.open("r", encoding="utf-8") as atlasfile:
        atlas = json.load(atlasfile)

    image_names = atlas['meta']['image'].split(',')
    image_paths = [atlas_path.parent / image_name for image_name in image_names]

    unpack_path = atlas_path.parent / (atlas_path.name + '_unpack')
    if not unpack_path.exists():
        os.mkdir(str(unpack_path))

    log_info('Write prefix.txt...', verbose, is_verbose=True)
    with (unpack_path / 'prefix.txt').open('w', encoding="utf-8") as prefixfile:
        prefixfile.write(atlas['meta']['prefix'])

    log_info('Split images...', verbose, is_verbose=True)
    for filename in atlas['frames']:
        frame = atlas['frames'][filename]
        image_pack = Image.open(str(image_paths[frame['frame']["idx"]]))
        image = image_pack.crop((frame['frame']['x'],
            frame['frame']['y'],
            frame['frame']['x'] + frame['frame']['w'],
            frame['frame']['y'] + frame['frame']['h']
        ))
        new_image = Image.new('RGBA', (frame['sourceSize']['w'], frame['sourceSize']['h']), (0, 0, 0, 0))
        new_image.paste(image, (frame['spriteSourceSize']['x'], frame['spriteSourceSize']['y']))

        log_debug(f'Write {filename}...', verbose)

        if filename.endswith('jpg'):
            new_image.convert('RGB').save(str(unpack_path / filename), 'JPEG')
        else:
            new_image.save(str(unpack_path / filename), 'PNG')
    log_info('Unpack complete', verbose, is_verbose=True)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        log_error('You must pass a single atlas path', verbose)
        sys.exit(-1)

    atlas_path = sys.argv[1]
    main(atlas_path)