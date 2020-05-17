pushd .
cd %~dp0..\..
call script\dev\merge_assets.bat
call script\dev\export_lqc.bat
call script\dev\update_translation.bat
popd