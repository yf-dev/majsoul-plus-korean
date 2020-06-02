#! /usr/bin/python
import json
import csv
from pathlib import Path
import os
lang = os.getenv('MAJSOUL_LANG', 'en')

def parse_node(translate_json_rows, node, path):
    if 'text' in node['props']:
        text = node['props']['text']
        if text:
            translate_json_rows.append([path, text, text])
    if 'child' in node:
        for i, child in enumerate(node['child']):
            parse_node(translate_json_rows, child, f'{path}|{i}')

def main(original_assets_path, translation_path):
    translate_json_rows = []

    with open(Path(original_assets_path) / 'uiconfig' / f'ui_{lang}.json', 'r', encoding='utf-8') as jsonfile:
        ui_en = json.load(jsonfile)
        for node_key in ui_en:
            parse_node(translate_json_rows, ui_en[node_key], node_key)

    templates_path = Path(translation_path) / 'templates'
    templates_path.mkdir(parents=True, exist_ok=True)

    with open(templates_path / 'translate_json.csv', 'w', encoding='utf-8-sig', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['location', 'source', 'target', 'translator_comments', 'developer_comments'])
        for row in translate_json_rows:
            csv_writer.writerow(row)

if __name__ == '__main__':
    main(
        str(Path('./dev-resources/assets-latest')),
        str(Path('./translation'))
    )