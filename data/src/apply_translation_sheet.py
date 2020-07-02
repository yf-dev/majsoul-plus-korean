#! /usr/bin/python
import csv
import re
from pathlib import Path
import os
from common import log_normal, log_debug, log_warn, log_info, log_error
lang = os.getenv('MAJSOUL_LANG', 'en')
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

def main(translation_path, temp_path):
    log_normal('Apply translate_sheet.csv to original csv files...', verbose)

    log_info('Read translate_sheet.csv...', verbose)
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
                log_debug(f'Open {sheet_path} to find target...', verbose)
                with open(temp_path / 'csv' / sheet_path, 'r', encoding='utf-8-sig') as sheetfile:
                    sheet_reader = csv.DictReader(sheetfile)
                    fieldnames = sheet_reader.fieldnames
                    if has_voice_path:
                        header, voice_path = header.split('(')
                        voice_path = voice_path[:-1]
                    
                    for sheet_row in sheet_reader:
                        if has_voice_path:
                            if sheet_row[header] == target and sheet_row['path'] == voice_path:
                                log_debug(f'Apply string to {sheet_path}...', verbose)
                                sheet_row[header] = translated
                        else:
                            if sheet_row[header] == target:
                                log_debug(f'Apply string to {sheet_path}...', verbose)
                                sheet_row[header] = translated
                        sheet_data.append(sheet_row)
                log_debug(f'Write {sheet_path}...', verbose)
                with open(temp_path / 'csv' / sheet_path, 'w', encoding='utf-8-sig', newline='') as sheetfile:
                    sheet_writer = csv.DictWriter(sheetfile, fieldnames=fieldnames)
                    sheet_writer.writeheader()
                    sheet_writer.writerows(sheet_data)
            except Exception as e:
                log_error(f'Error on line : {row}', verbose)
                raise e

    log_info('Apply complete', verbose)

if __name__ == '__main__':
    main(
        str(Path('./translation')),
        str(Path('./temp'))
    )