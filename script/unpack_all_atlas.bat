pushd .
cd %~dp0..
setlocal
if not defined MAJSOUL_LANG (
  set MAJSOUL_LANG=en
)
bin\unpack_all_atlas.exe
endlocal
popd