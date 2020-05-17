pushd .
cd %~dp0..
setlocal
if not defined MAJSOUL_LANG (
  set MAJSOUL_LANG=en
)
utils\protoc\bin\protoc.exe --proto_path=.\dev-resources\assets-latest\res\proto --python_out=.\src\generated config.proto
bin\generate_sheet_proto.exe
utils\protoc\bin\protoc.exe --proto_path=.\src\generated --python_out=.\src\generated sheets.proto
bin\export_sheets.exe
endlocal
popd