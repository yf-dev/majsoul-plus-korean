#! /usr/bin/python
import csv
import json
from pathlib import Path
import os
lang = os.getenv('MAJSOUL_LANG', 'en')

def main(translation_path, dist_path, temp_path):
    chars = set(chr(x) for x in range(32, 127))

    for csv_path in (Path(translation_path) / 'csv').glob('*.csv'):
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            is_header = True
            header = []
            header_text = []
            for row in csv_reader:
                if is_header:
                    header = row
                    for i, col in enumerate(header):
                        if col == lang or col.endswith(f'_{lang}'):
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
        if 'text' in node['props']:
            text = node['props']['text']
            if text:
                for char in text:
                    if char not in chars:
                        chars.add(char)
        if 'child' in node:
            for i, child in enumerate(node['child']):
                parse_node(child, f'{path}|{i}')

    with open(Path(dist_path) / 'assets' / 'uiconfig' / f'ui_{lang}.json', 'r', encoding='utf-8') as jsonfile:
        ui_en = json.load(jsonfile)
        for node_key in ui_en:
            parse_node(ui_en[node_key], node_key)

    sorted_chars = sorted(chars)
    with open(Path(temp_path) / 'chars.txt', 'w', encoding='utf-8') as charsfile:
        for char in sorted_chars:
            charsfile.write(char)

if __name__ == '__main__':
    main(
        str(Path('./translation')),
        str(Path('./dist/korean')),
        str(Path('./temp'))
    )