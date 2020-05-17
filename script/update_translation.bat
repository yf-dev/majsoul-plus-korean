pushd .
cd %~dp0..
bin\apply_translation_sheet.exe
bin\apply_translation_json.exe
bin\extract_chars.exe
bin\build_sheets.exe
call script\update_font.bat
popd