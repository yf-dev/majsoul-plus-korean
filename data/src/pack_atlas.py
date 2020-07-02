#! /usr/bin/python
from PIL import Image, ImageDraw
import json
import os
import sys
from pathlib import Path
from rectpack import newPacker, PackingMode
import re
from common import log_normal, log_debug, log_warn, log_info, log_error

verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

def export_image(atlas, atlas_unpack_path, target_path, images, positions, group_id, target_size, padding):
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
    new_image_path = target_path / new_image_name
    new_image.save(new_image_path, 'PNG')
    log_debug(new_image_path, verbose)
    return new_image_name

def main(size_factor, atlas_unpack_path, target_path):
    log_normal(f'Pack {atlas_unpack_path}...', verbose)
    atlas = {
        "frames": {},
        "meta": {}
    }
    
    atlas_unpack_path = Path(atlas_unpack_path)
    target_path = Path(target_path)
    target_path.mkdir(parents=True, exist_ok=True)

    log_info('Read prefix.txt...', verbose, is_verbose=True)
    with (atlas_unpack_path / 'prefix.txt').open('r', encoding="utf-8") as prefixfile:
        atlas['meta']['prefix'] = prefixfile.readline().strip()

    image_paths = list(sorted(atlas_unpack_path.glob('*.png')))
    image_paths += list(sorted(atlas_unpack_path.glob('*.jpg')))
    images = []
    max_width = 0
    max_height = 0

    log_info('Load images...', verbose, is_verbose=True)
    for image_path in image_paths:
        log_debug(f'Load {image_path}...', verbose)
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
    log_debug('Max size = {max_size}...', verbose)
    while max_size > (target_size - (padding * 2)):
        target_size *= 2

    log_debug('Target size = {max_size}...', verbose)

    image_sizes = [(image["frame"]["w"] + (padding * 2), image["frame"]["h"] + (padding * 2), i) for i, image in enumerate(images)]
    new_image_names = []

    log_info('Calculate packer...', verbose, is_verbose=True)
    packer = newPacker(mode=PackingMode.Offline, rotation=False)
    for image_size in image_sizes:
        packer.add_rect(*image_size)
    packer.add_bin(target_size - (padding * 2), target_size - (padding * 2), float("inf"))
    packer.pack()

    log_info('Generate packed images...', verbose, is_verbose=True)
    group_id = 0
    for abin in packer:
        image_group = []
        positions = []
        for rect in abin:
            image_group.append(images[rect.rid])
            positions.append((rect.x, rect.y))
            images[rect.rid] = None
        new_image_names.append(export_image(atlas, atlas_unpack_path, target_path, image_group, positions, group_id, target_size, padding))
        group_id += 1

    log_info('Write atlas...', verbose, is_verbose=True)
    atlas['meta']['image'] = ",".join(new_image_names)

    atlas_path = target_path / atlas_unpack_path.name[:-len('_unpack')]

    with atlas_path.open("w", encoding="utf-8") as atlasfile:
        json.dump(atlas, atlasfile, separators=(',', ':'), ensure_ascii=False)
    
    log_info('Pack complete', verbose, is_verbose=True)

if __name__ == '__main__':
    size_factor = 8
    target_path = ''

    if len(sys.argv) < 2:
        log_error('You must pass a single atlas_unpack path', verbose)
        sys.exit(-1)
    if len(sys.argv) > 4:
        log_error('Too many args', verbose)
        sys.exit(-1)
    if len(sys.argv) > 3:
        size_factor = int(sys.argv[3])
    if len(sys.argv) > 2:
        target_path = sys.argv[2]

    atlas_unpack_path = sys.argv[1]

    if not target_path:
        target_path = str(Path(atlas_unpack_path).parent)
    main(size_factor, atlas_unpack_path, target_path)