#! /usr/bin/python
import os
from pathlib import Path
lang = os.getenv('MAJSOUL_LANG', 'en')

def main(original_assets_path, temp_path):
    import_path = Path(temp_path) / 'proto' / 'config_pb2.py'
    with open(import_path, 'r', encoding='utf-8') as config_pb2_file:
        config_pb2_code = config_pb2_file.read()
        exec(config_pb2_code, globals())

    config_table = ConfigTables()
    lqc_path = Path(original_assets_path) / 'res' / 'config' / 'lqc.lqbin'
    with open(lqc_path, 'rb') as lqc:
        config_table.ParseFromString(lqc.read())

    new_proto = 'syntax = \"proto3\";\n\n'

    for schema in config_table.schemas:
        for sheet in schema.sheets:
            class_words = f'{schema.name}_{sheet.name}'.split('_')
            class_name = ''.join(name.capitalize() for name in class_words)
            new_proto += f'message {class_name} {{\n'
            for field in sheet.fields:
                new_proto += f'  {"repeated" if field.array_length > 0 else ""} {field.pb_type} {field.field_name} = {field.pb_index};\n'
            new_proto += '}\n\n'

    sheets_proto_path = Path(temp_path) / 'proto' / 'sheets.proto'
    with open(sheets_proto_path, 'w', encoding='utf-8') as sheets:
        sheets.write(new_proto)

if __name__ == '__main__':
    main(
        str(Path('./dev-resources/assets-latest')),
        str(Path('./temp'))
    )