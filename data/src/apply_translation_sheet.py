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

    sheets = {}

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

                if sheet_path not in sheets:
                    sheets[sheet_path] = {}

                has_voice_path = sheet_path == 'VoiceSound.csv' and '(' in header
                if has_voice_path:
                    header, voice_path = header.split('(')
                    voice_path = voice_path[:-1]
                    sheets[sheet_path][f'{target}|{header}|{voice_path}'] = {
                        'target': target,
                        'header': header,
                        'voice_path': voice_path,
                        'translated': translated,
                    }
                else:
                    sheets[sheet_path][f'{target}|{header}'] = {
                        'target': target,
                        'header': header,
                        'translated': translated,
                    }
            except Exception as e:
                log_error(f'Error on line : {row}', verbose)
                raise e
    
    log_info('Find targets on sheets...', verbose)
    for sheet_path in sheets:
        sheet_datas = sheets[sheet_path]
        new_sheet_data = []
        fieldnames = []
        target_datas = {}
        log_info(f'Open {sheet_path} to find target...', verbose)
        with open(temp_path / 'csv' / sheet_path, 'r', encoding='utf-8-sig') as sheetfile:
            sheet_reader = csv.DictReader(sheetfile)
            fieldnames = sheet_reader.fieldnames
            for sheet_row in sheet_reader:
                for header in fieldnames:
                    if sheet_path == 'VoiceSound.csv':
                        key = f'{sheet_row[header]}|{header}|{sheet_row["path"]}'
                    else:
                        key = f'{sheet_row[header]}|{header}'
                    if key in sheet_datas:
                        sheet_row[header] = sheet_datas[key]['translated']
                new_sheet_data.append(sheet_row)
    
        log_info(f'Write {sheet_path}...', verbose)
        with open(temp_path / 'csv' / sheet_path, 'w', encoding='utf-8-sig', newline='') as sheetfile:
            sheet_writer = csv.DictWriter(sheetfile, fieldnames=fieldnames)
            sheet_writer.writeheader()
            sheet_writer.writerows(new_sheet_data)

    log_info('Apply complete', verbose)

if __name__ == '__main__':
    main(
        str(Path('./translation')),
        str(Path('./temp'))
    )