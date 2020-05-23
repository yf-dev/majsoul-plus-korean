#! /usr/bin/python
import csv
import os
lang = os.getenv('MAJSOUL_LANG', 'en') 

with open(f'./src/translate_sheet.csv', 'r', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    is_header = True
    for row in csv_reader:
        if is_header:
            is_header = False
            continue
        try:
            sheet_path = row[0]
            header = row[1]
            target = row[2]
            translated = row[3]
            sheet_data = []
            fieldnames = []
            with open(sheet_path, 'r', encoding='utf-8') as sheetfile:
                sheet_reader = csv.DictReader(sheetfile)
                fieldnames = sheet_reader.fieldnames
                for sheet_row in sheet_reader:
                    if sheet_row[header] == target:
                        sheet_row[header] = translated
                    sheet_data.append(sheet_row)
            with open(sheet_path, 'w', encoding='utf-8', newline='') as sheetfile:
                sheet_writer = csv.DictWriter(sheetfile, fieldnames=fieldnames)
                sheet_writer.writeheader()
                sheet_writer.writerows(sheet_data)
        except Exception as e:
            print(f'[!] Error on line : {row}')
            raise e