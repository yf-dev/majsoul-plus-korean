#! /usr/bin/python
from pathlib import Path
import csv
import json
import re

from .common import log_normal, log_debug, log_warn, log_info, mpk_lang


def get_node(root, path_list):
    copied_path_list = list(path_list)
    node = root[copied_path_list.pop(0)]
    while copied_path_list:
        node = node["child"][int(copied_path_list.pop(0))]
    return node


def update_value(root, path_list, value):
    node = get_node(root, path_list)
    node["props"]["text"] = value

    copied_path_list = list(path_list)
    while len(copied_path_list) > 1:
        i = int(copied_path_list.pop())
        parent = get_node(root, copied_path_list)
        parent["child"][i] = node
        node = parent
    root[copied_path_list[0]] = node


def main(original_assets_path, translation_path, dist_path):
    log_normal(f"Apply translate_json.csv to ui_{mpk_lang}.json...")
    ui_en = None

    log_info(f"Read ui_{mpk_lang}.json...")
    with open(
        Path(original_assets_path) / "uiconfig" / f"ui_{mpk_lang}.json",
        "r",
        encoding="utf-8",
    ) as jsonfile:
        ui_en = json.load(jsonfile)

    log_info("Read translate_json.csv...")
    with open(
        Path(translation_path) / "translate_json.csv", "r", encoding="utf-8-sig"
    ) as csvfile:
        csv_reader = csv.reader(csvfile)

        log_info("Convert translate_json.csv...")
        is_header = True
        for row in csv_reader:
            if is_header:
                is_header = False
                continue
            path = row[0]
            target = re.sub(r"([^\\])\\n", r"\1\n", row[1]).replace("\\\\", "\\")
            translated = re.sub(r"([^\\])\\n", r"\1\n", row[2]).replace("\\\\", "\\")

            node = None
            try:
                log_debug(f"Convert {path}")
                node = get_node(ui_en, path.split("|"))
            except Exception:  # pylint: disable=broad-except
                log_warn(f"Cannot access {path}")
                continue

            if "text" not in node["props"]:
                log_warn(f"Node has not text on {path}: '{target}'")
                continue
            elif node["props"]["text"] != target:
                log_warn(
                    f"Target is not matched on {path}: '{node['props']['text']}' != '{target}'"
                )
                continue

            update_value(ui_en, path.split("|"), translated)

    log_info(f"Write ui_{mpk_lang}.json...")
    target_path = Path(dist_path) / "assets" / "uiconfig" / f"ui_{mpk_lang}.json"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as jsonfile:
        json.dump(ui_en, jsonfile, separators=(",", ":"), ensure_ascii=False)
    log_info("Apply complete")


if __name__ == "__main__":
    main(
        str(Path("./assets-original")),
        str(Path("./translation")),
        str(Path("./dist/korean")),
    )
