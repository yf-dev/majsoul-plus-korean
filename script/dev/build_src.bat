pushd .
cd %~dp0..\..
pipenv run pyinstaller --distpath .\bin --workpath .\build\apply_translation_json --onefile src\apply_translation_json.py
pipenv run pyinstaller --distpath .\bin --workpath .\build\apply_translation_sheet --onefile src\apply_translation_sheet.py
pipenv run pyinstaller --distpath .\bin --workpath .\build\build_sheets --onefile src\build_sheets.py
pipenv run pyinstaller --distpath .\bin --workpath .\build\combine_bitmapfont --onefile src\combine_bitmapfont.py
pipenv run pyinstaller --distpath .\bin --workpath .\build\export_sheets --onefile src\export_sheets.py
pipenv run pyinstaller --distpath .\bin --workpath .\build\extract_chars --onefile src\extract_chars.py
pipenv run pyinstaller --distpath .\bin --workpath .\build\generate_sheet_proto --onefile src\generate_sheet_proto.py
pipenv run pyinstaller --distpath .\bin --workpath .\build\generate_translation_json --onefile src\generate_translation_json.py
pipenv run pyinstaller --distpath .\bin --workpath .\build\generate_translation_sheet --onefile src\generate_translation_sheet.py
pipenv run pyinstaller --distpath .\bin --workpath .\build\merge_assets --onefile src\merge_assets.py
popd