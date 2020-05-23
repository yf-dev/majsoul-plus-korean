pushd .
cd %~dp0..\..
setlocal
if not defined MAJSOUL_LANG (
  set MAJSOUL_LANG=en
)
call script\dev\pack_all_atlas.bat
pipenv run python src\export_sheets.py
pipenv run python src\apply_translation_sheet.py
pipenv run python src\apply_translation_json.py
pipenv run python src\extract_chars.py
pipenv run python src\build_sheets.py
call script\dev\update_font.bat
endlocal
popd