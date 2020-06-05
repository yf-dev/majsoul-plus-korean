#! /usr/bin/python
import os
from pathlib import Path
import csv
import re
import polib
from datetime import datetime
lang = os.getenv('MAJSOUL_LANG', 'en')

HASH_LEN = 32

def main(translation_path):
    translation_path = Path(translation_path)

    json_entries = []
    sheet_entries = []

    po = polib.pofile(
        translation_path / f'translate_ko.po',
        encoding='utf-8'
    )

    for entry in po.translated_entries():
        if entry.msgid.startswith('json|'):
            json_entries.append(entry)
        elif entry.msgid.startswith('sheet|'):
            sheet_entries.append(entry)
        else:
            raise Exception(f'Unexpected msgid: {entry.msgid}')

    with open(translation_path / 'translate_json.csv', 'w', encoding='utf-8-sig', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['location', 'source', 'target'])
        for entry in json_entries:
            path = entry.msgid[len('json|'):-(HASH_LEN + 1)]
            target = entry.msgctxt.replace('\\', '\\\\').replace('\n', '\\n')
            translated = entry.msgstr.replace('\\', '\\\\').replace('\n', '\\n')
            csv_writer.writerow([path, target, translated])

    with open(translation_path / 'translate_sheet.csv', 'w', encoding='utf-8-sig', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['location', 'context', 'source', 'target'])
        for entry in sheet_entries:
            full_path = entry.msgid[len('sheet|'):-(HASH_LEN + 1)]
            sheet_path = '|'.join(full_path.split('|')[:-1])
            header = full_path.split('|')[-1]
            target = entry.msgctxt.replace('\\', '\\\\').replace('\n', '\\n')
            translated = entry.msgstr.replace('\\', '\\\\').replace('\n', '\\n')
            csv_writer.writerow([sheet_path, header, target, translated])

if __name__ == '__main__':
    main(
        str(Path('./translation'))
    )