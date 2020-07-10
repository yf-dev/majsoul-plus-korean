#! /usr/bin/python
import json
import csv
from pathlib import Path
import os
from common import log_normal, log_debug, log_warn, log_info, log_error
lang = os.getenv('MAJSOUL_LANG', 'en')
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

def parse_node(translate_json_rows, node, path):
    if 'text' in node['props']:
        text = node['props']['text'].replace('\\', '\\\\').replace('\n', '\\n')
        if text:
            translate_json_rows.append([path, text, text])
    if 'child' in node:
        for i, child in enumerate(node['child']):
            parse_node(translate_json_rows, child, f'{path}|{i}')

def main(original_assets_path, translation_path):
    log_normal('Generate translate_json.csv...', verbose)
    translate_json_rows = []

    log_info(f'Read ui_{lang}.json...', verbose)
    with open(Path(original_assets_path) / 'uiconfig' / f'ui_{lang}.json', 'r', encoding='utf-8') as jsonfile:
        ui_en = json.load(jsonfile)
        for node_key in ui_en:
            parse_node(translate_json_rows, ui_en[node_key], node_key)

    log_info('Write translate_json.csv...', verbose)
    templates_path = Path(translation_path) / 'templates'
    templates_path.mkdir(parents=True, exist_ok=True)

    with open(templates_path / 'translate_json.csv', 'w', encoding='utf-8-sig', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['location', 'source', 'target'])
        for row in translate_json_rows:
            csv_writer.writerow(row)

    log_info('Generate complete', verbose)

if __name__ == '__main__':
    main(
        str(Path('./assets-original')),
        str(Path('./translation'))
    )