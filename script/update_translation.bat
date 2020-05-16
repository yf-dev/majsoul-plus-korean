pushd .
cd %~dp0..
pipenv run python src\apply_translation_sheet.py
pipenv run python src\apply_translation_json.py
pipenv run python src\extract_chars.py
pipenv run python src\build_sheets.py
call script\update_font.bat
popd