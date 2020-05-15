#! /usr/bin/python
import csv
from pathlib import Path
from generated import config_pb2, sheets_pb2

config_table = config_pb2.ConfigTables()
with open("./dev-resources/assets-latest/res/config/lqc.lqbin", "rb") as lqc:
    config_table.ParseFromString(lqc.read())

Path("./src/generated/csv").mkdir(parents=True, exist_ok=True)

for data in config_table.datas:
    class_words = f"{data.table}_{data.sheet}".split("_")
    class_name = "".join(name.capitalize() for name in class_words)

    with open(f'./src/generated/csv/{class_name}.csv', 'w', encoding='utf-8', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([x.name for x in getattr(sheets_pb2, class_name)().DESCRIPTOR.fields])
        
        if not hasattr(data, 'data'):
            continue

        for field_msg in data.data:
            field = getattr(sheets_pb2, class_name)()
            field.ParseFromString(field_msg)
            row = []
            for x in getattr(sheets_pb2, class_name)().DESCRIPTOR.fields:
                if hasattr(field, x.name):
                    row.append(getattr(field, x.name))
                else:
                    row.append(None)
            csv_writer.writerow(row)
