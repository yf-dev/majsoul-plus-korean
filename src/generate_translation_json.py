#! /usr/bin/python
import json
import csv
from pathlib import Path

translate_json_rows = []

def parse_node(node, path):
    if 'text' in node['props']:
        text = node['props']['text']
        if text:
            translate_json_rows.append([path, text, text])
    if 'child' in node:
        for i, child in enumerate(node['child']):
            parse_node(child, f'{path}|{i}')

with open('./dev-resources/assets-latest/uiconfig/ui_en.json', 'r', encoding='utf-8') as jsonfile:
    ui_en = json.load(jsonfile)
    for node_key in ui_en:
        parse_node(ui_en[node_key], node_key)

with open(f'./src/generated/translate_json_template.csv', 'w', encoding='utf-8', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['path', 'target', 'translated'])
    for row in translate_json_rows:
        csv_writer.writerow(row)