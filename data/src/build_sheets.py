#! /usr/bin/python
import csv
from google.protobuf.descriptor import FieldDescriptor
from pathlib import Path
import json
import os
lang = os.getenv('MAJSOUL_LANG', 'en') 

def main(original_assets_path, translation_path, dist_path, temp_path):
    target_csvs = []

    with open(Path(translation_path) / 'translate_sheet.csv', 'r', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.reader(csvfile)
        is_header = True
        for row in csv_reader:
            if is_header:
                is_header = False
                continue
            if row[0] not in target_csvs:
                target_csvs.append(row[0])

    import_config_path = Path(temp_path) / 'proto' / 'config_pb2.py'
    with open(import_config_path, 'r', encoding='utf-8') as config_pb2_file:
        config_pb2_code = config_pb2_file.read()
        exec(config_pb2_code, globals())

    import_sheets_path = Path(temp_path) / 'proto' / 'sheets_pb2.py'
    with open(import_sheets_path, 'r', encoding='utf-8') as sheets_pb2_file:
        sheets_pb2_code = sheets_pb2_file.read()
        exec(sheets_pb2_code, globals())
        

    config_table = ConfigTables()
    with open(Path(original_assets_path) / 'res' / 'config' / 'lqc.lqbin', "rb") as lqc:
        config_table.ParseFromString(lqc.read())

    for data_index in range(len(config_table.datas)):
        data = config_table.datas[data_index]
        class_words = f"{data.table}_{data.sheet}".split("_")
        class_name = "".join(name.capitalize() for name in class_words)

        csv_path = Path(temp_path) / 'csv' / f'{class_name}.csv'

        if not csv_path.is_file():
            print(f'[!] This csv is not exist: {csv_path}')
            continue

        if csv_path.name not in target_csvs:
            print(f'[.] Skip {csv_path}')
            continue

        print(f'[+] Building {csv_path}')

        csv_path = str(csv_path) # for matching csv format

        with open(csv_path, 'r', encoding='utf-8-sig') as csvfile:
            csv_reader = csv.reader(csvfile)
            del data.data[:]
            header = []
            is_header = True
            for row in csv_reader:
                if is_header:
                    header = row
                    is_header = False
                    continue
                field = globals()[class_name]()
                for i, col in enumerate(header):
                    value = row[i]
                    fd = field.DESCRIPTOR.fields_by_name[col]
                    if fd.label == FieldDescriptor.LABEL_REPEATED:
                        getattr(field, col).extend(json.loads(value))
                    else:
                        field_type = fd.type
                        if field_type in [
                            FieldDescriptor.TYPE_INT32,
                            FieldDescriptor.TYPE_INT64,
                            FieldDescriptor.TYPE_SINT32,
                            FieldDescriptor.TYPE_SINT64,
                            FieldDescriptor.TYPE_UINT32,
                            FieldDescriptor.TYPE_UINT64,
                            ]:
                            value = int(value)
                        elif field_type in [
                            FieldDescriptor.TYPE_DOUBLE,
                            FieldDescriptor.TYPE_FIXED32,
                            FieldDescriptor.TYPE_FIXED64,
                            FieldDescriptor.TYPE_FLOAT,
                            ]:
                            value = float(value)
                        setattr(field, col, value)
                data.data.append(field.SerializeToString())

    target_path = Path(dist_path) / 'assets' / 'res' / 'config' / 'lqc.lqbin'
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "wb") as lqc:
        lqc.write(config_table.SerializeToString())

if __name__ == '__main__':
    main(
        str(Path('./dev-resources/assets-latest')),
        str(Path('./translation')),
        str(Path('./dist/korean')),
        str(Path('./temp'))
    )