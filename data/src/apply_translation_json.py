#! /usr/bin/python
import csv
from pathlib import Path
import json
import os
lang = os.getenv('MAJSOUL_LANG', 'en') 

def get_node(root, path_list):
    p = list(path_list)
    node = root[p.pop(0)]
    while p:
        node = node['child'][int(p.pop(0))]
    return node

def update_value(root, path_list, value):
    node = get_node(root, path_list)
    node['props']['text'] = value
    
    p = list(path_list)
    while len(p) > 1:
        i = int(p.pop())
        parent = get_node(root, p)
        parent['child'][i] = node
        node = parent
    root[p[0]] = node

def main(original_assets_path, translation_path, dist_path):
    ui_en = None
    with open(Path(original_assets_path) / 'uiconfig' / f'ui_{lang}.json', 'r', encoding='utf-8') as jsonfile:
        ui_en = json.load(jsonfile)

    with open(Path(translation_path) / 'translate_json.csv', 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        is_header = True
        for row in csv_reader:
            if is_header:
                is_header = False
                continue
            path = row[0]
            target = row[1]
            translated = row[2]

            node = None
            try:
                node = get_node(ui_en, path.split('|'))
            except Exception as e:
                print(f'Cannot access {path}')
                continue

            if node['props']['text'] != target:
                print(f"Target is not matched on {path}: '{node['props']['text']}' != '{target}'")
                continue
            
            update_value(ui_en, path.split('|'), translated)

    target_path = Path(dist_path) / 'assets' / 'uiconfig' / f'ui_{lang}.json'
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(ui_en, jsonfile, separators=(',', ':'), ensure_ascii=False)

if __name__ == '__main__':
    main(
        str(Path('./dev-resources/assets-latest')),
        str(Path('./translation')),
        str(Path('./dist/korean'))
    )