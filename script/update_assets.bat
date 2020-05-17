pushd .
cd %~dp0..
setlocal
if not defined MAJSOUL_LANG (
  set MAJSOUL_LANG=en
)
call script\merge_assets.bat
call script\export_lqc.bat
call script\update_translation.bat
endlocal
popd