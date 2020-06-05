#! /usr/bin/python
import os
from pathlib import Path
import csv
import re
import polib
from datetime import datetime
from hashlib import md5
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

            if not target:
                continue

            entry = polib.POEntry(
                msgctxt=target,
                msgid=f'json|{path}|{md5(target.encode()).hexdigest()}',
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

            if not target:
                continue

            entry = polib.POEntry(
                msgctxt=target,
                msgid=f'sheet|{sheet_path}|{header}|{md5(target.encode()).hexdigest()}',
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