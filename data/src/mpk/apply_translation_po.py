#! /usr/bin/python
from pathlib import Path
import csv
import polib

from .common import log_normal, log_debug, log_info, mpk_lang
from .models.text import (
    TranslationDataset,
    UiJsonTranslator,
    XinshouyindaoJsonTranslator,
    BytesTranslator,
    CsvTranslator,
)

HASH_LEN = 32


def main(translation_path, original_assets_path, dist_path, temp_path):
    log_normal("Apply translate_ko.po to game objects...")
    translation_path = Path(translation_path)

    translated_dataset = TranslationDataset("ko")
    translated_dataset.read_pofile(
        translation_path / f"translate_{mpk_lang}.po", mpk_lang
    )
    translated_dataset.read_pofile(translation_path / "translate_ko.po", "ko")

    log_info("Write ui json files...")
    ui_json_translator = UiJsonTranslator()
    ui_json_translator.translation_dataset = translated_dataset
    ui_json_translator.save_to_game_objects(original_assets_path, dist_path)

    log_info("Write xinshouyindao json files...")
    xinshouyindao_json_translator = XinshouyindaoJsonTranslator()
    xinshouyindao_json_translator.translation_dataset = translated_dataset
    xinshouyindao_json_translator.save_to_game_objects(original_assets_path, dist_path)

    log_info("Write bytes files...")
    bytes_translator = BytesTranslator()
    bytes_translator.translation_dataset = translated_dataset
    bytes_translator.save_to_game_objects(original_assets_path, dist_path)

    log_info("Write csv files...")
    csv_translator = CsvTranslator()
    csv_translator.translation_dataset = translated_dataset
    csv_translator.save_to_game_objects(temp_path, None)

    log_info("Apply complete")


if __name__ == "__main__":
    main(
        str(Path("./translation")),
        str(Path("./assets-original")),
        str(Path("./dist/korean")),
        str(Path("./temp")),
    )
