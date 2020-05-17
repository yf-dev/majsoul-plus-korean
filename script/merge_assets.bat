pushd .
cd %~dp0..
setlocal
if not defined MAJSOUL_LANG (
  set MAJSOUL_LANG=en
)
bin\merge_assets.exe
endlocal
popd