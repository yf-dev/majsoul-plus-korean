@echo off

pushd .
cd %~dp0.
setlocal

powershell -File update.ps1

endlocal
popd