pushd .
cd %~dp0..\..
setlocal
if not defined MAJSOUL_LANG (
  set MAJSOUL_LANG=en
)
call script\dev\merge_assets.bat
call script\dev\export_lqc.bat
call script\dev\update_translation.bat
endlocal
popd