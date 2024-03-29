#! /usr/bin/python
from pathlib import Path
import csv
import json
from google.protobuf.descriptor import FieldDescriptor

from .common import log_normal, log_debug, log_warn, log_info


def main(original_assets_path, translation_path, dist_path, temp_path):
    log_normal("Build csv files into lqc.lqbin...")

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
    with open(Path(original_assets_path) / "res" / "config" / "lqc.lqbin", "rb") as lqc:
        config_table.ParseFromString(lqc.read())

    log_info("Read original tables...")
    for data_index in range(len(config_table.datas)):
        data = config_table.datas[data_index]
        class_words = f"{data.table}_{data.sheet}".split("_")
        class_name = "".join(name.capitalize() for name in class_words)

        csv_path = Path(temp_path) / "csv" / f"{class_name}.csv"

        if not csv_path.is_file():
            log_warn(f"This csv is not exist: {csv_path}")
            continue

        log_info(f"Build {csv_path}...")

        csv_path = str(csv_path)  # for matching csv format

        log_debug(f"Read {csv_path}...")
        with open(csv_path, "r", encoding="utf-8-sig") as csvfile:
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
                    field_descriptor = field.DESCRIPTOR.fields_by_name[col]
                    if field_descriptor.label == FieldDescriptor.LABEL_REPEATED:
                        getattr(field, col).extend(json.loads(value))
                    else:
                        field_type = field_descriptor.type
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

    log_info("Write lqc.lqbin...")
    target_path = Path(dist_path) / "assets" / "res" / "config" / "lqc.lqbin"
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "wb") as lqc:
        lqc.write(config_table.SerializeToString())

    log_info("Build complete")


if __name__ == "__main__":
    main(
        str(Path("./assets-original")),
        str(Path("./translation")),
        str(Path("./dist/korean")),
        str(Path("./temp")),
    )
