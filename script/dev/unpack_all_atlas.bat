pushd .
cd %~dp0..\..
setlocal
if not defined MAJSOUL_LANG (
  set MAJSOUL_LANG=en
)
pipenv run python src\unpack_all_atlas.py
endlocal
popd