#! /usr/bin/python
import csv
from google.protobuf.descriptor import FieldDescriptor
from pathlib import Path
from generated import config_pb2, sheets_pb2
import json
import os
lang = os.getenv('MAJSOUL_LANG', 'en') 

target_csvs = []

with open(f'./src/translate_sheet.csv', 'r', encoding='utf-8') as csvfile:
    csv_reader = csv.reader(csvfile)
    is_header = True
    for row in csv_reader:
        if is_header:
            is_header = False
            continue
        if row[0] not in target_csvs:
            target_csvs.append(row[0])
    

config_table = config_pb2.ConfigTables()
with open("./dev-resources/assets-latest/res/config/lqc.lqbin", "rb") as lqc:
    config_table.ParseFromString(lqc.read())

for data_index in range(len(config_table.datas)):
    data = config_table.datas[data_index]
    class_words = f"{data.table}_{data.sheet}".split("_")
    class_name = "".join(name.capitalize() for name in class_words)

    csv_path = Path(f'./src/generated/csv/{class_name}.csv')

    if not csv_path.is_file():
        continue

    csv_path = str(csv_path) # for matching csv format

    if csv_path not in target_csvs:
        continue

    print(f'Building {csv_path}')

    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        del data.data[:]
        header = []
        is_header = True
        for row in csv_reader:
            if is_header:
                header = row
                is_header = False
                continue
            field = getattr(sheets_pb2, class_name)()
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

with open("./assets/res/config/lqc.lqbin", "wb") as lqc:
    lqc.write(config_table.SerializeToString())
