#! /usr/bin/python
import csv
from pathlib import Path
import os
lang = os.getenv('MAJSOUL_LANG', 'en')

def main(translation_path, temp_path):
    translate_sheet_rows = []

    csv_dir_path = Path(temp_path) / 'csv'
    for csv_path in sorted(csv_dir_path.glob('*.csv')):
        with open(csv_path, 'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.reader(csvfile)
            is_header = True
            header = []
            header_to_translate = []
            for row in csv_reader:
                if is_header:
                    header = row
                    for i, col in enumerate(header):
                        if col == lang or col.endswith(f'_{lang}'):
                            header_to_translate.append(i)
                    if not header_to_translate:
                        break
                    is_header = False
                    continue
                
                for col_index in header_to_translate:
                    translate_sheet_rows.append('|'.join([
                        csv_path.name,
                        header[col_index],
                        row[col_index].replace('\\', '\\\\').replace('\n', '\\n')
                    ]))

    # unique element
    translate_sheet_rows = list(dict.fromkeys(translate_sheet_rows))

    templates_path = Path(translation_path) / 'templates'
    templates_path.mkdir(parents=True, exist_ok=True)

    with open(templates_path / 'translate_sheet.csv', 'w', encoding='utf-8-sig', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['location', 'context', 'source', 'target', 'notes', 'developer comments'])
        for row in translate_sheet_rows:
            r = row.split('|')
            csv_writer.writerow(r + [r[2], None, None])

if __name__ == '__main__':
    main(
        str(Path('./translation')),
        str(Path('./temp'))
    )
