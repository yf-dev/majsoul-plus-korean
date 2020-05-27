#! /usr/bin/python
import os
from pathlib import Path
from common import run_cmd
from shutil import copyfile

lang = os.getenv('MAJSOUL_LANG', 'en') 

fonts = {
    'en': {
        'en_hanyi': ('SSRockRegular.ttf', 40),
        'en_haolong': ('BMEULJIROTTF.ttf', 35),
        'en_shuhun': ('SDKukdetopokki-aLt.otf', 35)
    },
    'jp': {
        'jp_haolong': ('NotoSansCJKkr-Medium.otf', 40),
        'jp_jiye': ('NotoSansCJKkr-Medium.otf', 35)
    }
}

def call_fontbm(font_file, font_name, font_size, fontbm_path, fonts_path, temp_path):
    texture_size = 2 ** 10
    while True:
        result = run_cmd([
            str(fontbm_path),
            f'--font-file={fonts_path / font_file}',
            f'--output={temp_path / "fonts" / font_name}',
            f'--chars-file={temp_path / "chars.txt"}',
            '--data-format=xml',
            '--spacing-vert=1',
            '--spacing-horiz=1',
            '--max-texture-count=1',
            f'--texture-width={texture_size}',
            f'--texture-height={texture_size}',
            f'--font-size={font_size}'
        ], False)
        if result:
            break
        texture_size *= 2

def main(dist_path, fonts_path, temp_path, fontbm_path):
    dist_path = Path(dist_path)
    fonts_path = Path(fonts_path)
    temp_path = Path(temp_path)
    fontbm_path = Path(fontbm_path)
    (temp_path / 'fonts').mkdir(parents=True, exist_ok=True)

    for font_name in fonts[lang]:
        font_data = fonts[lang][font_name]
        call_fontbm(
            font_data[0],
            font_name,
            font_data[1],
            fontbm_path,
            fonts_path,
            temp_path
        )
    
    from combine_bitmapfont import main as combine_bitmapfont
    combine_bitmapfont(
        str(dist_path),
        str(temp_path)
    )

    dist_font_path = dist_path / 'assets' / 'bitmapfont' / lang
    dist_font_path.mkdir(parents=True, exist_ok=True)
    for font_name in fonts[lang]:
        copyfile(temp_path / 'fonts' / f'{font_name}.fnt', dist_font_path / f'{font_name}.fnt')


if __name__ == '__main__':
    main(
        str(Path('./dist/korean')),
        str(Path('./fonts')),
        str(Path('./temp')),
        str(Path('./utils/fontbm/fontbm.exe'))
    )