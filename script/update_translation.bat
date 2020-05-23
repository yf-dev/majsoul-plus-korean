pushd .
cd %~dp0..
setlocal
if not defined MAJSOUL_LANG (
  set MAJSOUL_LANG=en
)
call script\pack_all_atlas.bat
bin\export_sheets.exe
bin\apply_translation_sheet.exe
bin\apply_translation_json.exe
bin\extract_chars.exe
bin\build_sheets.exe
call script\update_font.bat
endlocal
popd