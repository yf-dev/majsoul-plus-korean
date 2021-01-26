#! /usr/bin/python
from pathlib import Path

from .common import log_normal, log_info, mpk_lang
from .models.text import TranslationDataset


def main(translation_path, temp_path):
    log_normal("Extract characters from assets...")

    log_info("Add defualt ASCII characters...")
    chars = set(chr(x) for x in range(32, 127))

    log_info("Read characters from po files...")
    translation_path = Path(translation_path)

    translated_dataset = TranslationDataset("ko")
    translated_dataset.read_pofile(
        translation_path / f"translate_{mpk_lang}.po", mpk_lang
    )
    translated_dataset.read_pofile(translation_path / "translate_ko.po", "ko")

    for translation_string in translated_dataset.translation_string_map.values():
        target = translation_string.get_string(mpk_lang)
        if target is not None:
            for char in target.text:
                if char not in chars:
                    chars.add(char)
        translated = translation_string.get_string("ko")
        if translated is not None:
            for char in translated.text:
                if char not in chars:
                    chars.add(char)

    log_info("Write characters to chars.txt...")
    sorted_chars = sorted(chars)
    with open(Path(temp_path) / "chars.txt", "w", encoding="utf-8") as charsfile:
        for char in sorted_chars:
            charsfile.write(char)
    log_info("Extract complete")


if __name__ == "__main__":
    main(str(Path("./translation")), str(Path("./temp")))
