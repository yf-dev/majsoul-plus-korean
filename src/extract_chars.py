#! /usr/bin/python
import csv
from pathlib import Path

chars = set()

for csv_path in Path("./src/generated/csv").glob('*.csv'):
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        is_header = True
        header = []
        header_text = []
        for row in csv_reader:
            if is_header:
                header = row
                for i, col in enumerate(header):
                    if col == 'en' or col.endswith('_en'):
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

sorted_chars = sorted(chars)
with open("./src/generated/chars.txt", 'w', encoding='utf-8') as charsfile:
    for char in sorted_chars:
        charsfile.write(char)