pushd .
cd %~dp0..\..
setlocal
if not defined MAJSOUL_LANG (
  set MAJSOUL_LANG=en
)
pipenv run python src\generate_translation_sheet.py
pipenv run python src\generate_translation_json.py
endlocal
popd