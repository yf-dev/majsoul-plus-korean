pushd .
cd %~dp0..\..
utils\protoc\bin\protoc.exe --proto_path=.\dev-resources\assets-latest\res\proto --python_out=.\src\generated config.proto
pipenv run python src\generate_sheet_proto.py
utils\protoc\bin\protoc.exe --proto_path=.\src\generated --python_out=.\src\generated sheets.proto
pipenv run python src\export_sheets.py
popd