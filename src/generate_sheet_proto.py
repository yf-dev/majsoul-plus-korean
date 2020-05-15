#! /usr/bin/python
from generated import config_pb2

config_table = config_pb2.ConfigTables()
with open("./dev-resources/assets-latest/res/config/lqc.lqbin", "rb") as lqc:
    config_table.ParseFromString(lqc.read())

new_proto = "syntax = \"proto3\";\n\n"

for schema in config_table.schemas:
    for sheet in schema.sheets:
        class_words = f"{schema.name}_{sheet.name}".split("_")
        class_name = "".join(name.capitalize() for name in class_words)
        new_proto += f"message {class_name} {{\n"
        for field in sheet.fields:
            new_proto += f"  {'repeated' if field.array_length > 0 else ''} {field.pb_type} {field.field_name} = {field.pb_index};\n"
        new_proto += "}\n\n"

with open("./src/generated/sheets.proto", "w", encoding="utf-8") as sheets:
    sheets.write(new_proto)