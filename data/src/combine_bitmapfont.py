#! /usr/bin/python
from PIL import Image
import json
import os
from pathlib import Path
lang = os.getenv('MAJSOUL_LANG', 'en')

def main(dist_path, fonts_path, temp_path):
    with open(Path(fonts_path) / 'fontmap.json', 'r', encoding='utf-8') as fontmap:
        fonts = json.load(fontmap)[lang].keys()

    font_images = []

    for font in fonts:
        font_images.append(Image.open(Path(temp_path) / 'fonts' / f'{font}_0.png'))

    total_width = sum(font_image.size[0] for font_image in font_images)
    total_height = max(font_image.size[1] for font_image in font_images)

    new_image = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))

    x_pos = 0
    for font_image in font_images:
        new_image.paste(font_image, (x_pos, 0))
        x_pos += font_image.size[0]

    bitmapfont_path = Path(dist_path) / 'assets' / 'res' / 'atlas' / 'bitmapfont'
    bitmapfont_path.mkdir(parents=True, exist_ok=True)

    new_image.save(bitmapfont_path / f'{lang}.png', "PNG")

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

if __name__ == '__main__':
    main(
        str(Path('./dist/korean')),
        str(Path('./fonts')),
        str(Path('./temp')),
    )
