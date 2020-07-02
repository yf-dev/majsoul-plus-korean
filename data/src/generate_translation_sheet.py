#! /usr/bin/python
import csv
from pathlib import Path
import os
from common import log_normal, log_debug, log_warn, log_info, log_error
lang = os.getenv('MAJSOUL_LANG', 'en')
verbose = int(os.getenv('MAJSOUL_VERBOSE', 0)) == 1

def main(translation_path, temp_path):
    log_normal('Generate translate_sheet.csv...', verbose)
    translate_sheet_rows = []

    log_info('Read csv files...', verbose)
    csv_dir_path = Path(temp_path) / 'csv'
    for csv_path in sorted(csv_dir_path.glob('*.csv')):
        log_info(f'Read {csv_path}...', verbose)
        with open(csv_path, 'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.reader(csvfile)
            is_header = True
            header = []
            header_to_translate = []
            voice_path_idx = None
            for row in csv_reader:
                if is_header:
                    header = row
                    for i, col in enumerate(header):
                        if col == lang or col.endswith(f'_{lang}'):
                            header_to_translate.append(i)
                        if csv_path.name == 'VoiceSound.csv' and col == 'path':
                            voice_path_idx = i
                    if not header_to_translate:
                        break
                    is_header = False
                    continue
                
                for col_index in header_to_translate:
                    context = header[col_index]
                    if csv_path.name == 'VoiceSound.csv':
                        context = f'{context}({row[voice_path_idx]})'
                    translate_sheet_rows.append('|'.join([
                        csv_path.name,
                        context,
                        row[col_index].replace('\\', '\\\\').replace('\n', '\\n')
                    ]))

    # unique element
    translate_sheet_rows = list(dict.fromkeys(translate_sheet_rows))

    log_info('Write translate_sheet.csv...', verbose)
    templates_path = Path(translation_path) / 'templates'
    templates_path.mkdir(parents=True, exist_ok=True)

    with open(templates_path / 'translate_sheet.csv', 'w', encoding='utf-8-sig', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['location', 'context', 'source', 'target'])
        for row in translate_sheet_rows:
            r = row.split('|')
            csv_writer.writerow(r + [r[2]])
    
    log_info('Generate complete', verbose)

if __name__ == '__main__':
    main(
        str(Path('./translation')),
        str(Path('./temp'))
    )
