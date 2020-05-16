#! /usr/bin/python
import csv
import json


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

ui_en = None
with open('./dev-resources/assets-latest/uiconfig/ui_en.json', 'r', encoding='utf-8') as jsonfile:
    ui_en = json.load(jsonfile)

with open(f'./src/translate_json.csv', 'r', encoding='utf-8') as csvfile:
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
            print(f"Target is not matched on {path}: '{node['props']['text']}' != 'target'")
            continue
        
        update_value(ui_en, path.split('|'), translated)

with open('./assets/uiconfig/ui_en.json', 'w', encoding='utf-8') as jsonfile:
    json.dump(ui_en, jsonfile, separators=(',', ':'), ensure_ascii=False)