pushd .
cd %~dp0..\..
setlocal
if not defined MAJSOUL_LANG (
  set MAJSOUL_LANG=en
)
bin\generate_translation_sheet.exe
bin\generate_translation_json.exe
endlocal
popd