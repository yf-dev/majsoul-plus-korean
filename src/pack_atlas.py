#! /usr/bin/python
from PIL import Image, ImageDraw
import json
import os
import sys
from pathlib import Path
from rectpack import newPacker, PackingMode
import re

size_factor = 8

def export_image(images, positions, group_id, target_size, padding):
    new_image = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
    for i, image in enumerate(images):
        position = positions[i]
        real_position = (position[0] + padding, position[1] + padding)
        name = image['path'].name
        new_image.paste(
            image['cropped_data'],
            real_position
        )
        colors = image['cropped_data'].getcolors(2)
        if (colors and len(colors) == 1):
            draw = ImageDraw.Draw(new_image)
            draw.rectangle((
                real_position[0] - 1,
                real_position[1] - 1,
                real_position[0] + image['frame']['w'],
                real_position[1] + image['frame']['h']
            ), width=1, outline=colors[0][1])
            # print(colors)
        del image['path']
        del image['cropped_data']
        image['frame']['idx'] = group_id
        image['frame']['x'] = real_position[0]
        image['frame']['y'] = real_position[1]
        atlas['frames'][name] = image
    group_number = group_id if group_id > 0 else ''
    new_image_name = f"{atlas_unpack_path.name[:-len('.atlas_unpack')]}{group_number}.png"
    new_image_path = atlas_unpack_path.parent / new_image_name
    new_image.save(new_image_path, 'PNG')
    print(new_image_path)
    return new_image_name

if len(sys.argv) < 2:
    print('You must pass a single atlas_unpack path')
    sys.exit(-1)
if len(sys.argv) > 2:
    size_factor = int(sys.argv[2])
if len(sys.argv) > 3:
    print('Too many args')
    sys.exit(-1)

atlas_unpack_path = Path(sys.argv[1])

atlas = {
    "frames": {},
    "meta": {}
}

with (atlas_unpack_path / 'prefix.txt').open('r', encoding="utf-8") as prefixfile:
    atlas['meta']['prefix'] = prefixfile.readline().strip()

image_paths = list(atlas_unpack_path.glob('*.png'))
image_paths += list(atlas_unpack_path.glob('*.jpg'))
images = []
max_width = 0
max_height = 0

for image_path in image_paths:
    image_data = Image.open(image_path)
    width, height = image_data.size
    box = image_data.getbbox()
    if box is None:
        left, top, right, bottom = (0, 0, width, height)
        cropped_image = image_data
        cropped_width, cropped_height = width, height
    else:
        left, top, right, bottom = box
        cropped_image = image_data.crop((left, top, right, bottom))
        cropped_width, cropped_height = cropped_image.size

    if max_width < cropped_width:
        max_width = cropped_width

    if max_height < cropped_height:
        max_height = cropped_height

    x_offset = 0
    y_offset = 0
    w_offset = 0
    h_offset = 0
    m = re.search(r'(\[([+-]?\d+),\s*([+-]?\d+),\s*([+-]?\d+),\s*([+-]?\d+)\])\.png$', image_path.name)
    if m:
        x_offset = int(m.group(2))
        y_offset = int(m.group(3))
        w_offset = int(m.group(4))
        h_offset = int(m.group(5))
        image_path = image_path.parent / image_path.name.replace(m.group(1), '')
    
    images.append({
        "path": image_path,
        "cropped_data": cropped_image,
        "frame": {
            "h": cropped_height,
            "w": cropped_width,
        },
        "sourceSize": {
            "h": height + h_offset,
            "w": width + w_offset
        },
        "spriteSourceSize": {
            "x": left + x_offset,
            "y": top + y_offset
        }
    })

padding = 2

target_size = 2 ** size_factor
max_size = max(max_height, max_width)
print(f'max_size = {max_size}')
while max_size > (target_size - (padding * 2)):
    target_size *= 2

print(f'target_size = {target_size}')

image_sizes = [(image["frame"]["w"] + (padding * 2), image["frame"]["h"] + (padding * 2), i) for i, image in enumerate(images)]
new_image_names = []

packer = newPacker(mode=PackingMode.Offline, rotation=False)
for image_size in image_sizes:
	packer.add_rect(*image_size)
packer.add_bin(target_size - (padding * 2), target_size - (padding * 2), float("inf"))
packer.pack()

group_id = 0
for abin in packer:
    image_group = []
    positions = []
    for rect in abin:
        image_group.append(images[rect.rid])
        positions.append((rect.x, rect.y))
        images[rect.rid] = None
    new_image_names.append(export_image(image_group, positions, group_id, target_size, padding))
    group_id += 1

atlas['meta']['image'] = ",".join(new_image_names)

atlas_path = atlas_unpack_path.parent / atlas_unpack_path.name[:-len('_unpack')]

with atlas_path.open("w", encoding="utf-8") as atlasfile:
    json.dump(atlas, atlasfile, separators=(',', ':'), ensure_ascii=False)