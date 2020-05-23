#! /usr/bin/python
from PIL import Image
import json
import os
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print('You must pass a single atlas path')
    sys.exit(-1)

atlas_path = Path(sys.argv[1])

atlas = None

with atlas_path.open("r", encoding="utf-8") as atlasfile:
    atlas = json.load(atlasfile)

image_names = atlas['meta']['image'].split(',')
image_paths = [atlas_path.parent / image_name for image_name in image_names]

unpack_path = atlas_path.parent / (atlas_path.name + '_unpack')
if not unpack_path.exists():
    os.mkdir(str(unpack_path))

with (unpack_path / 'prefix.txt').open('w', encoding="utf-8") as prefixfile:
    prefixfile.write(atlas['meta']['prefix'])

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

    if filename.endswith('jpg'):
        new_image.convert('RGB').save(str(unpack_path / filename), 'JPEG')
    else:
        new_image.save(str(unpack_path / filename), 'PNG')