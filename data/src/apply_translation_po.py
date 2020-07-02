#! /usr/bin/python
import os
from pathlib import Path
import csv
import re
import polib
from datetime import datetime
from common import log_normal, log_debug, log_warn, log_info, log_error
lang = os.getenv('MAJSOUL_LANG', 'en')
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

HASH_LEN = 32

def main(translation_path):
    log_normal('Apply translate_ko.po to translate_json.csv and translate_sheet.csv...', verbose)
    translation_path = Path(translation_path)

    json_entries = []
    sheet_entries = []

    log_info('Read translate_ko.po...', verbose)
    po = polib.pofile(
        translation_path / f'translate_ko.po',
        encoding='utf-8'
    )

    log_info('Split entries...', verbose)
    for entry in po.translated_entries():
        if entry.msgid.startswith('json|'):
            log_debug(f'Add {entry.msgid} to json data', verbose)
            json_entries.append(entry)
        elif entry.msgid.startswith('sheet|'):
            log_debug(f'Add {entry.msgid} to sheet data', verbose)
            sheet_entries.append(entry)
        else:
            error_msg = f'Unexpected msgid: {entry.msgid}'
            log_error(error_msg, verbose)
            raise Exception(error_msg)
    
    log_info('Write translate_json.csv...', verbose)
    with open(translation_path / 'translate_json.csv', 'w', encoding='utf-8-sig', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        log_info('Write translate_json.csv rows...', verbose)
        csv_writer.writerow(['location', 'source', 'target'])
        for entry in json_entries:
            path = entry.msgid[len('json|'):-(HASH_LEN + 1)]
            target = entry.msgctxt.replace('\\', '\\\\').replace('\n', '\\n')
            translated = entry.msgstr.replace('\\', '\\\\').replace('\n', '\\n')
            log_debug(f'Write {entry.msgid} to {path}', verbose)
            csv_writer.writerow([path, target, translated])

    log_info('Write translate_sheet.csv...', verbose)
    with open(translation_path / 'translate_sheet.csv', 'w', encoding='utf-8-sig', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        log_info('Write translate_sheet.csv rows...', verbose)
        csv_writer.writerow(['location', 'context', 'source', 'target'])
        for entry in sheet_entries:
            full_path = entry.msgid[len('sheet|'):-(HASH_LEN + 1)]
            sheet_path = '|'.join(full_path.split('|')[:-1])
            header = full_path.split('|')[-1]
            target = entry.msgctxt.replace('\\', '\\\\').replace('\n', '\\n')
            translated = entry.msgstr.replace('\\', '\\\\').replace('\n', '\\n')
            log_debug(f'Write {entry.msgid} to {sheet_path}', verbose)
            csv_writer.writerow([sheet_path, header, target, translated])

    log_info('Apply complete', verbose)

if __name__ == '__main__':
    main(
        str(Path('./translation'))
    )