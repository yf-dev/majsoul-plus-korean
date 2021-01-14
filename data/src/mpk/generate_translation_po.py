#! /usr/bin/python
from pathlib import Path
import csv
import json

from .common import AVAILABLE_LANGS, log_info, mpk_lang
from .models.text import TranslationDataset


def parse_ui_json_node(json_rows, node, path):
    if "text" in node["props"]:
        text = node["props"]["text"]
        if text:
            json_rows.append((path, text))
    if "child" in node:
        for i, child in enumerate(node["child"]):
            parse_ui_json_node(json_rows, child, f"{path}|{i}")


def parse_ui_json(json_paths):
    t_string_data = TranslationDataset(mpk_lang)
    source_type = "json-ui"
    for json_path in json_paths:
        log_info(f"Read {json_path}...")
        source_filepath = json_path.name
        language = json_path.name[len("ui_") : -len(".json")]
        with open(json_path, "r", encoding="utf-8") as jsonfile:
            json_data = json.load(jsonfile)
        json_rows = []
        for node_key in json_data:
            parse_ui_json_node(json_rows, json_data[node_key], node_key)
        for context, text in json_rows:
            t_string_data.set(source_type, context, source_filepath, 0, language, text)
    return t_string_data


def parse_xinshouyindao_json(json_paths):
    t_string_data = TranslationDataset(mpk_lang)
    source_type = "json-xinshouyindao"
    for json_path in json_paths:
        log_info(f"Read {json_path}...")
        source_filepath = json_path.name
        language = json_path.name[len("xinshouyindao_") : -len(".json")]
        with open(json_path, "r", encoding="utf-8") as jsonfile:
            json_data = json.load(jsonfile)
        for page in json_data["datas"]:
            page_id = "_".join(page["page_id"].split("_")[1:])
            t_string_data.set(
                source_type,
                f"{page_id}|name",
                source_filepath,
                0,
                language,
                page["name"],
            )
            t_string_data.set(
                source_type,
                f"{page_id}|text",
                source_filepath,
                0,
                language,
                page["text"],
            )
    return t_string_data


def parse_bytes(bytes_paths):
    t_string_data = TranslationDataset(mpk_lang)
    source_type = "bytes"
    for bytes_path in bytes_paths:
        log_info(f"Read {bytes_path}...")
        source_filepath = f"{bytes_path.parent.name}/{bytes_path.name}"
        language = bytes_path.name[len("100004_") : -len(".bytes")]
        with open(bytes_path, "r", encoding="utf-8-sig") as bytesfile:
            source_lineno = 1
            for line in bytesfile:
                splited = line.split(":")
                line_id = splited[0]
                text = ":".join(splited[1:])
                context = f"{source_filepath[:-(1 + len(language) + len('.bytes'))]}|{line_id}"
                t_string_data.set(
                    source_type, context, source_filepath, source_lineno, language, text
                )
                source_lineno += 1
    return t_string_data


def parse_csv(csv_path):
    t_string_data = TranslationDataset(mpk_lang)
    source_type = "sheet"
    source_filepath = csv_path.name
    log_info(f"Read {csv_path}...")
    with open(csv_path, "r", encoding="utf-8-sig") as csvfile:
        csv_reader = csv.DictReader(csvfile)

        has_voice_path = False
        header_prefixs = []
        for fieldname in csv_reader.fieldnames:
            if fieldname == mpk_lang or fieldname.endswith(f"_{mpk_lang}"):
                header_prefixs.append(fieldname[: -len(mpk_lang)])
            if fieldname == "path" and csv_path.name == "VoiceSound.csv":
                has_voice_path = True

        source_lineno = 2
        for row in csv_reader:
            for header_prefix in header_prefixs:
                context = f"{header_prefix}{mpk_lang}"
                if has_voice_path:
                    context = f"{context}({row['path']})"

                for language in AVAILABLE_LANGS:
                    header = f"{header_prefix}{language}"
                    if header in row:
                        t_string_data.set(
                            source_type,
                            context,
                            source_filepath,
                            source_lineno,
                            language,
                            row[header],
                        )
            source_lineno += 1
    return t_string_data


def main(translation_path, original_assets_path, temp_path):
    t_string_datas = []

    log_info("Read ui json files...")
    ui_json_dir_path = Path(original_assets_path) / "uiconfig"
    t_string_datas.append(parse_ui_json(sorted(ui_json_dir_path.glob("ui_*.json"))))

    log_info("Read xinshouyindao json files...")
    xinshouyindao_json_dir_path = Path(original_assets_path) / "docs"
    t_string_datas.append(
        parse_xinshouyindao_json(
            sorted(xinshouyindao_json_dir_path.glob("xinshouyindao_*.json"))
        )
    )

    log_info("Read bytes files...")
    bytes_dir_path = Path(original_assets_path) / "docs" / "spot"
    t_string_datas.append(parse_bytes(sorted(bytes_dir_path.glob("**/*.bytes"))))

    log_info("Read csv files...")
    csv_dir_path = Path(temp_path) / "csv"
    for csv_path in sorted(csv_dir_path.glob("*.csv")):
        t_string_datas.append(parse_csv(csv_path))

    merged = TranslationDataset.merge(t_string_datas)
    merged.write_pofiles(Path(translation_path))


if __name__ == "__main__":
    main(
        str(Path("./translation")),
        str(Path("./assets-original")),
        str(Path("./temp")),
    )
