pushd .
cd %~dp0..
call script\merge_assets.bat
call script\export_lqc.bat
call script\update_translation.bat
popd