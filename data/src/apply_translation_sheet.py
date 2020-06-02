#! /usr/bin/python
import csv
import re
from pathlib import Path
import os
lang = os.getenv('MAJSOUL_LANG', 'en')

def main(translation_path, temp_path):
    temp_path = Path(temp_path)
    with open(Path(translation_path) / 'translate_sheet.csv', 'r', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.reader(csvfile)
        is_header = True
        for row in csv_reader:
            if is_header:
                is_header = False
                continue
            try:
                sheet_path = row[0]
                header = row[1]
                target = re.sub(r'([^\\])\\n', r'\1\n', row[2]).replace('\\\\', '\\')
                translated = re.sub(r'([^\\])\\n', r'\1\n', row[3]).replace('\\\\', '\\')
                sheet_data = []
                fieldnames = []
                with open(temp_path / 'csv' / sheet_path, 'r', encoding='utf-8-sig') as sheetfile:
                    sheet_reader = csv.DictReader(sheetfile)
                    fieldnames = sheet_reader.fieldnames
                    for sheet_row in sheet_reader:
                        if sheet_row[header] == target:
                            sheet_row[header] = translated
                        sheet_data.append(sheet_row)
                with open(temp_path / 'csv' / sheet_path, 'w', encoding='utf-8-sig', newline='') as sheetfile:
                    sheet_writer = csv.DictWriter(sheetfile, fieldnames=fieldnames)
                    sheet_writer.writeheader()
                    sheet_writer.writerows(sheet_data)
            except Exception as e:
                print(f'[!] Error on line : {row}')
                raise e

if __name__ == '__main__':
    main(
        str(Path('./translation')),
        str(Path('./temp'))
    )