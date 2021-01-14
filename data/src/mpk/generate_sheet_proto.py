#! /usr/bin/python
from pathlib import Path

from .common import log_normal, log_info


def main(original_assets_path, temp_path):
    log_normal("Generate sheets.proto...")

    log_info("Load config_pb2.py...")
    import_path = Path(temp_path) / "proto" / "config_pb2.py"
    with open(import_path, "r", encoding="utf-8") as config_pb2_file:
        config_pb2_code = config_pb2_file.read()
        exec(config_pb2_code, globals())  # pylint: disable=exec-used

    log_info("Load tables from lqc.lqbin...")
    config_table = ConfigTables()  # pylint: disable=undefined-variable
    lqc_path = Path(original_assets_path) / "res" / "config" / "lqc.lqbin"
    with open(lqc_path, "rb") as lqc:
        config_table.ParseFromString(lqc.read())

    log_info("Create proto data...")

    new_proto = 'syntax = "proto3";\n\n'

    for schema in config_table.schemas:
        for sheet in schema.sheets:
            class_words = f"{schema.name}_{sheet.name}".split("_")
            class_name = "".join(name.capitalize() for name in class_words)
            new_proto += f"message {class_name} {{\n"
            for field in sheet.fields:
                new_proto += f'  {"repeated" if field.array_length > 0 else ""} {field.pb_type} {field.field_name} = {field.pb_index};\n'
            new_proto += "}\n\n"

    log_info("Write sheets.proto...")
    sheets_proto_path = Path(temp_path) / "proto" / "sheets.proto"
    with open(sheets_proto_path, "w", encoding="utf-8") as sheets:
        sheets.write(new_proto)

    log_info("Generate complete")


if __name__ == "__main__":
    main(str(Path("./assets-original")), str(Path("./temp")))
