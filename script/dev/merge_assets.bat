pushd .
cd %~dp0..\..
pipenv run python src\merge_assets.py
popd