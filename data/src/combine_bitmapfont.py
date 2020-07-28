#! /usr/bin/python
from PIL import Image
import json
import os
from pathlib import Path
from common import log_normal, log_debug, log_warn, log_info, log_error
lang = os.getenv('MAJSOUL_LANG', 'en')
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

def main(dist_path, fonts_path, temp_path):
    log_normal('Combine bitmap font files into single file...', verbose)

    log_info('Read fontmap.json...', verbose)
    with open(Path(fonts_path) / 'fontmap.json', 'r', encoding='utf-8') as fontmap:
        fonts = json.load(fontmap)[lang].keys()

    font_images = []

    log_info('Read font images...', verbose)
    for font in fonts:
        font_image_path = Path(temp_path) / 'fonts' / f'{font}_0.png'
        log_info(f'Read {font_image_path}...', verbose)
        font_images.append(Image.open(font_image_path))

    total_height = max(font_image.size[1] for font_image in font_images)
    image_size = total_height


    log_info('Generate new font image...', verbose)
    new_image = Image.new('RGBA', (image_size, image_size), (0, 0, 0, 0))

    x_pos = 0
    for font_image in font_images:
        new_image.paste(font_image, (x_pos, 0))
        x_pos += font_image.size[0]

    log_info('Write new font image...', verbose)
    bitmapfont_path = Path(dist_path) / 'assets' / 'res' / 'atlas' / 'bitmapfont'
    bitmapfont_path.mkdir(parents=True, exist_ok=True)

    new_image.save(bitmapfont_path / f'{lang}.png', "PNG")

    log_info('Write new font atlas...', verbose)
    with open(bitmapfont_path / f"{lang}.atlas", "w", encoding="utf-8") as atlasfile:
        atlas = {
            "frames": {},
            "meta": {
                "image": f"{lang}.png",
                "prefix": f"bitmapfont/{lang}/"
            }
        }
        x_pos = 0
        for i, font in enumerate(fonts):
            font_image = font_images[i]
            atlas["frames"][f"{font}.png"] = {
                "frame": {
                    "h": font_image.size[1],
                    "idx": 0,
                    "w": font_image.size[0],
                    "x": x_pos,
                    "y": 0
                },
                "sourceSize": {
                    "h": font_image.size[1],
                    "w": font_image.size[0]
                },
                "spriteSourceSize": {
                    "x": 0,
                    "y": 0
                }
            }
            x_pos += font_image.size[0]
        json.dump(atlas, atlasfile, separators=(',', ':'))

    log_info('Combine complete', verbose)

if __name__ == '__main__':
    main(
        str(Path('./dist/korean')),
        str(Path('./fonts')),
        str(Path('./temp')),
    )
