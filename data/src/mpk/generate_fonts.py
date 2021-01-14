#! /usr/bin/python
from pathlib import Path
from shutil import copyfile
import json

from .combine_bitmapfont import main as combine_bitmapfont
from .common import run_cmd, log_normal, log_debug, log_info, mpk_lang


def call_fontbm(
    font_file, font_name, font_size, fontbm_path, fonts_path, temp_path, num_of_font
):
    texture_size = 2 ** 10
    while True:
        cmd = [
            str(fontbm_path),
            f"--font-file={fonts_path / font_file}",
            f'--output={temp_path / "fonts" / font_name}',
            f'--chars-file={temp_path / "chars.txt"}',
            "--data-format=xml",
            "--spacing-vert=1",
            "--spacing-horiz=1",
            "--max-texture-count=1",
            f"--texture-width={int(texture_size / num_of_font)}",
            f"--texture-height={texture_size}",
            f"--font-size={font_size}",
        ]
        log_debug(f'Call {" ".join(cmd)}')
        result = run_cmd(cmd, False)
        if result:
            break
        texture_size *= 2


def main(dist_path, fonts_path, temp_path, fontbm_path):
    log_normal("Generate font images...")

    dist_path = Path(dist_path)
    fonts_path = Path(fonts_path)
    temp_path = Path(temp_path)
    fontbm_path = Path(fontbm_path)
    (temp_path / "fonts").mkdir(parents=True, exist_ok=True)

    log_info("Read fontmap.json...")
    with open(fonts_path / "fontmap.json", "r", encoding="utf-8") as fontmap:
        fonts = json.load(fontmap)

    for font_name in fonts[mpk_lang]:
        log_info(f"Generate font image for {font_name}...")
        font_data = fonts[mpk_lang][font_name]
        call_fontbm(
            font_data[0],
            font_name,
            font_data[1],
            fontbm_path,
            fonts_path,
            temp_path,
            len(fonts[mpk_lang]),
        )

    combine_bitmapfont(str(dist_path), str(fonts_path), str(temp_path))

    log_info("Copy fnt files...")
    dist_font_path = dist_path / "assets" / "bitmapfont" / mpk_lang
    dist_font_path.mkdir(parents=True, exist_ok=True)
    for font_name in fonts[mpk_lang]:
        copyfile(
            temp_path / "fonts" / f"{font_name}.fnt",
            dist_font_path / f"{font_name}.fnt",
        )

    log_info("Generate comlete")


if __name__ == "__main__":
    main(
        str(Path("./dist/korean")),
        str(Path("./fonts")),
        str(Path("./temp")),
        str(Path("./utils/fontbm/fontbm.exe")),
    )
