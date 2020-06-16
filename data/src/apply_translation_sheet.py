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
                has_voice_path = sheet_path == 'VoiceSound.csv' and '(' in header
                with open(temp_path / 'csv' / sheet_path, 'r', encoding='utf-8-sig') as sheetfile:
                    sheet_reader = csv.DictReader(sheetfile)
                    fieldnames = sheet_reader.fieldnames
                    if has_voice_path:
                        header, voice_path = header.split('(')
                        voice_path = voice_path[:-1]
                    
                    for sheet_row in sheet_reader:
                        if has_voice_path:
                            if sheet_row[header] == target and sheet_row['path'] == voice_path:
                                sheet_row[header] = translated
                        else:
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