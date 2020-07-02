#! /usr/bin/python
import csv
from pathlib import Path
import re
import json
import os
from common import log_normal, log_debug, log_warn, log_info
lang = os.getenv('MAJSOUL_LANG', 'en') 
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

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
    log_normal(f'Apply translate_json.csv to ui_{lang}.json...', verbose)
    ui_en = None

    log_info(f'Read ui_{lang}.json...', verbose)
    with open(Path(original_assets_path) / 'uiconfig' / f'ui_{lang}.json', 'r', encoding='utf-8') as jsonfile:
        ui_en = json.load(jsonfile)

    log_info('Read translate_json.csv...', verbose)
    with open(Path(translation_path) / 'translate_json.csv', 'r', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.reader(csvfile)

        log_info('Convert translate_json.csv...', verbose)
        is_header = True
        for row in csv_reader:
            if is_header:
                is_header = False
                continue
            path = row[0]
            target = re.sub(r'([^\\])\\n', r'\1\n', row[1]).replace('\\\\', '\\')
            translated = re.sub(r'([^\\])\\n', r'\1\n', row[2]).replace('\\\\', '\\')

            node = None
            try:
                log_debug(f'Convert {path}', verbose)
                node = get_node(ui_en, path.split('|'))
            except Exception as e:
                log_warn(f'Cannot access {path}', verbose)
                continue
            
            if 'text' not in node['props']:
                log_warn(f"Node has not text on {path}: '{target}'", verbose)
                continue
            elif node['props']['text'] != target:
                log_warn(f"Target is not matched on {path}: '{node['props']['text']}' != '{target}'", verbose)
                continue
            
            update_value(ui_en, path.split('|'), translated)

    log_info(f'Write ui_{lang}.json...', verbose)
    target_path = Path(dist_path) / 'assets' / 'uiconfig' / f'ui_{lang}.json'
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(ui_en, jsonfile, separators=(',', ':'), ensure_ascii=False)
    log_info('Apply complete', verbose)

if __name__ == '__main__':
    main(
        str(Path('./dev-resources/assets-latest')),
        str(Path('./translation')),
        str(Path('./dist/korean'))
    )