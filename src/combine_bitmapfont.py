#! /usr/bin/python
from PIL import Image
import json
import os
lang = os.getenv('MAJSOUL_LANG', 'en')

if lang == 'jp':
    fonts = [
        'jp_haolong',
        'jp_jiye'
    ]
else: # en
    fonts = [
        'en_hanyi',
        'en_haolong',
        'en_shuhun'
    ]

font_images = []

for font in fonts:
    font_images.append(Image.open(f"./src/generated/fonts/{font}_0.png"))

total_width = sum(font_image.size[0] for font_image in font_images)
total_height = max(font_image.size[1] for font_image in font_images)

new_image = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))

x_pos = 0
for font_image in font_images:
    new_image.paste(font_image, (x_pos, 0))
    x_pos += font_image.size[0]

new_image.save(f"./assets/res/atlas/bitmapfont/{lang}.png", "PNG")

with open(f"./assets/res/atlas/bitmapfont/{lang}.atlas", "w", encoding="utf-8") as atlasfile:
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
