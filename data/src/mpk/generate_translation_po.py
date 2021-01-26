#! /usr/bin/python
from pathlib import Path

from .common import log_info
from .models.text import (
    TranslationDataset,
    UiJsonTranslator,
    XinshouyindaoJsonTranslator,
    BytesTranslator,
    CsvTranslator,
)


def main(translation_path, original_assets_path, temp_path):
    translation_datasets = []

    log_info("Read ui json files...")
    ui_json_translator = UiJsonTranslator()
    ui_json_translator.load_from_game_objects(original_assets_path)
    translation_datasets.append(ui_json_translator.translation_dataset)

    log_info("Read xinshouyindao json files...")
    xinshouyindao_json_translator = XinshouyindaoJsonTranslator()
    xinshouyindao_json_translator.load_from_game_objects(original_assets_path)
    translation_datasets.append(xinshouyindao_json_translator.translation_dataset)

    log_info("Read bytes files...")
    bytes_translator = BytesTranslator()
    bytes_translator.load_from_game_objects(original_assets_path)
    translation_datasets.append(bytes_translator.translation_dataset)

    log_info("Read csv files...")
    csv_translator = CsvTranslator()
    csv_translator.load_from_game_objects(temp_path)
    translation_datasets.append(csv_translator.translation_dataset)

    merged = TranslationDataset.merge(translation_datasets)
    merged.write_pofiles(Path(translation_path))


if __name__ == "__main__":
    main(
        str(Path("./translation")),
        str(Path("./assets-original")),
        str(Path("./temp")),
    )
