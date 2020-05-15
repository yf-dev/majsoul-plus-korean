#! /usr/bin/python
from PIL import Image

en_hanyi_0 = Image.open("./src/generated/fonts/en_hanyi_0.png")
en_haolong_0 = Image.open("./src/generated/fonts/en_haolong_0.png")
en_shuhun_0 = Image.open("./src/generated/fonts/en_shuhun_0.png")

new_image = Image.new('RGBA', (
    en_hanyi_0.size[0] + en_haolong_0.size[0] + en_shuhun_0.size[0],
    max(en_hanyi_0.size[1], en_haolong_0.size[1], en_shuhun_0.size[1])
    ), (0, 0, 0, 0))

new_image.paste(en_hanyi_0, (0, 0))
new_image.paste(en_haolong_0, (en_hanyi_0.size[0], 0))
new_image.paste(en_shuhun_0, (en_hanyi_0.size[0] + en_haolong_0.size[0], 0))

new_image.save("./assets/res/atlas/bitmapfont/en.png", "PNG")