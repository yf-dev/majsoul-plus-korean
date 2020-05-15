#! /usr/bin/python
import csv
from pathlib import Path

translate_sheet_rows = []

for csv_path in Path("./src/generated/csv").glob('*.csv'):
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        is_header = True
        header = []
        header_to_translate = []
        for row in csv_reader:
            if is_header:
                header = row
                for i, col in enumerate(header):
                    if col == 'en' or col.endswith('_en'):
                        header_to_translate.append(i)
                if not header_to_translate:
                    break
                is_header = False
                continue
            
            for col_index in header_to_translate:
                translate_sheet_rows.append('|'.join([
                    str(csv_path),
                    header[col_index],
                    row[col_index]
                ]))

# unique element
translate_sheet_rows = list(dict.fromkeys(translate_sheet_rows))

with open(f'./src/generated/translate_sheet_template.csv', 'w', encoding='utf-8', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['path', 'header', 'target', 'translated'])
    for row in translate_sheet_rows:
        r = row.split('|')
        csv_writer.writerow(r + [r[2]])