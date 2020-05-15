#! /usr/bin/python
import csv
from pathlib import Path
from generated import config_pb2, sheets_pb2
from google.protobuf.descriptor import FieldDescriptor
from google.protobuf import any_pb2

config_table = config_pb2.ConfigTables()
with open("./dev-resources/assets-latest/res/config/lqc.lqbin", "rb") as lqc:
    original_msg = lqc.read()
    config_table.ParseFromString(original_msg)

for data in config_table.datas:
    class_words = f"{data.table}_{data.sheet}".split("_")
    class_name = "".join(name.capitalize() for name in class_words)


    if not hasattr(data, 'data'):
        continue

    for field_msg in data.data:
        field1 = getattr(sheets_pb2, class_name)()
        field1.ParseFromString(field_msg)

        field2 = getattr(sheets_pb2, class_name)()

        row = []
        for x in getattr(sheets_pb2, class_name)().DESCRIPTOR.fields:
            value = str(getattr(field1, x.name))
            field_type = x.type
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
            setattr(field2, x.name, value)

        result_msg = field2.SerializeToString()

        if field_msg != result_msg:
            print(class_name)
            print(field_msg.hex())
            a = any_pb2.Any()
            a.ParseFromString(field_msg)
            print(a.SerializeToString().hex())
            print(field1.SerializeToString().hex())
            print(result_msg.hex())
            import ipdb;ipdb.set_trace()
            input()