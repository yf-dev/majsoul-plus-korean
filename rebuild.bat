@echo off

pushd .
cd %~dp0.
setlocal

majsoul-plus-korean.exe all
pause

endlocal
popd