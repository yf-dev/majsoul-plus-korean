pushd .
cd %~dp0..
setlocal
if not defined MAJSOUL_LANG (
  set MAJSOUL_LANG=en
)
bin\apply_translation_sheet.exe
bin\apply_translation_json.exe
bin\extract_chars.exe
bin\build_sheets.exe
call script\update_font.bat
endlocal
popd