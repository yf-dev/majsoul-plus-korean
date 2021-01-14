#! /usr/bin/python
from pathlib import Path
import csv
import json

from .common import log_normal, log_info, mpk_lang


def main(dist_path, temp_path):
    log_normal("Extract characters from assets...")

    log_info("Add defualt ASCII characters...")
    chars = set(chr(x) for x in range(32, 127))

    log_info("Read characters from csv files...")
    for csv_path in sorted((Path(temp_path) / "csv").glob("*.csv")):
        with open(csv_path, "r", encoding="utf-8-sig") as csvfile:
            csv_reader = csv.reader(csvfile)
            is_header = True
            header = []
            header_text = []
            for row in csv_reader:
                if is_header:
                    header = row
                    for i, col in enumerate(header):
                        if col == mpk_lang or col.endswith(f"_{mpk_lang}"):
                            header_text.append(i)
                    if not header_text:
                        break
                    is_header = False
                    continue

                for col_index in header_text:
                    text = row[col_index]
                    for char in text:
                        if char not in chars:
                            chars.add(char)

    def parse_node(node, path):
        if "text" in node["props"]:
            text = node["props"]["text"]
            if text:
                for char in text:
                    if char not in chars:
                        chars.add(char)
        if "child" in node:
            for i, child in enumerate(node["child"]):
                parse_node(child, f"{path}|{i}")

    log_info(f"Read characters from ui_{mpk_lang}.json...")
    with open(
        Path(dist_path) / "assets" / "uiconfig" / f"ui_{mpk_lang}.json",
        "r",
        encoding="utf-8",
    ) as jsonfile:
        ui_en = json.load(jsonfile)
        for node_key in ui_en:
            parse_node(ui_en[node_key], node_key)

    log_info("Write characters to chars.txt...")
    sorted_chars = sorted(chars)
    with open(Path(temp_path) / "chars.txt", "w", encoding="utf-8") as charsfile:
        for char in sorted_chars:
            charsfile.write(char)
    log_info("Extract complete")


if __name__ == "__main__":
    main(str(Path("./dist/korean")), str(Path("./temp")))
