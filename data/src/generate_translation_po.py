#! /usr/bin/python
import os
from pathlib import Path
import csv
import re
import polib
from datetime import datetime
lang = os.getenv('MAJSOUL_LANG', 'en')

def main(translation_path):
    translation_path = Path(translation_path)

    po = polib.POFile(encoding='utf-8')
    po.metadata = {
        'PO-Revision-Date': f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S%z")}',
        'MIME-Version': '1.0',
        'Language': lang,
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
    }

    with open(translation_path / 'templates'/ 'translate_json.csv', 'r', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.reader(csvfile)
        is_header = True
        for row in csv_reader:
            if is_header:
                is_header = False
                continue
            path = row[0]
            target = re.sub(r'([^\\])\\n', r'\1\n', row[1]).replace('\\\\', '\\')
            translated = re.sub(r'([^\\])\\n', r'\1\n', row[2]).replace('\\\\', '\\')

            entry = polib.POEntry(
                msgctxt=f'json|{path}',
                msgid=target,
                msgstr=translated,
                occurrences=[('translate_json.csv', csv_reader.line_num)],
                encoding='utf-8'
            )
            po.append(entry)

    with open(translation_path / 'templates'/ 'translate_sheet.csv', 'r', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.reader(csvfile)
        is_header = True
        for row in csv_reader:
            if is_header:
                is_header = False
                continue

            sheet_path = row[0]
            header = row[1]
            target = re.sub(r'([^\\])\\n', r'\1\n', row[2]).replace('\\\\', '\\')
            translated = re.sub(r'([^\\])\\n', r'\1\n', row[3]).replace('\\\\', '\\')

            entry = polib.POEntry(
                msgctxt=f'sheet|{sheet_path}|{header}',
                msgid=target,
                msgstr=translated,
                occurrences=[('translate_sheet.csv', csv_reader.line_num)],
                encoding='utf-8'
            )
            po.append(entry)
    
    po.save(translation_path / f'translate_{lang}.po')

if __name__ == '__main__':
    main(
        str(Path('./translation'))
    )