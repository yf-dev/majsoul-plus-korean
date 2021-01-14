#! /usr/bin/python
from pathlib import Path
import csv
import json
from google.protobuf.descriptor import FieldDescriptor

from .common import log_normal, log_info


def main(original_assets_path, temp_path):
    log_normal("Export csv files from lqc.lqbin...")

    log_info("Load config_pb2.py...")
    import_config_path = Path(temp_path) / "proto" / "config_pb2.py"
    with open(import_config_path, "r", encoding="utf-8") as config_pb2_file:
        config_pb2_code = config_pb2_file.read()
        exec(config_pb2_code, globals())  # pylint: disable=exec-used

    log_info("Load sheets_pb2.py...")
    import_sheets_path = Path(temp_path) / "proto" / "sheets_pb2.py"
    with open(import_sheets_path, "r", encoding="utf-8") as sheets_pb2_file:
        sheets_pb2_code = sheets_pb2_file.read()
        exec(sheets_pb2_code, globals())  # pylint: disable=exec-used

    log_info("Load tables from lqc.lqbin...")
    config_table = ConfigTables()  # pylint: disable=undefined-variable
    lqc_path = Path(original_assets_path) / "res" / "config" / "lqc.lqbin"
    with open(lqc_path, "rb") as lqc:
        config_table.ParseFromString(lqc.read())

    csv_path = Path(temp_path) / "csv"
    csv_path.mkdir(parents=True, exist_ok=True)

    for data in config_table.datas:
        class_words = f"{data.table}_{data.sheet}".split("_")
        class_name = "".join(name.capitalize() for name in class_words)
        klass = globals()[class_name]

        log_info(f"Write {class_name}.csv...")
        with open(
            csv_path / f"{class_name}.csv", "w", encoding="utf-8-sig", newline=""
        ) as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([x.name for x in klass().DESCRIPTOR.fields])

            if not hasattr(data, "data"):
                continue

            for field_msg in data.data:
                field = klass()
                field.ParseFromString(field_msg)
                row = []
                for descriptor_field in klass().DESCRIPTOR.fields:
                    if hasattr(field, descriptor_field.name):
                        value = getattr(field, descriptor_field.name)
                        if descriptor_field.label == FieldDescriptor.LABEL_REPEATED:
                            value = json.dumps(list(value))
                        row.append(value)
                    else:
                        row.append(None)
                csv_writer.writerow(row)
    log_info("Export complete")


if __name__ == "__main__":
    main(str(Path("./assets-original")), str(Path("./temp")))
