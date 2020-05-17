pushd .
cd %~dp0..
rmdir src\generated\fonts /s /q
mkdir src\generated\fonts
utils\fontbm\fontbm.exe --font-file fonts\SSRockRegular.ttf --output src\generated\fonts\en_hanyi --chars-file src\generated\chars.txt --data-format xml --max-texture-count=1 --texture-width=512 --texture-height=1024 --font-size=40
utils\fontbm\fontbm.exe --font-file fonts\BMEULJIROTTF.ttf --output src\generated\fonts\en_haolong --chars-file src\generated\chars.txt --data-format xml --max-texture-count=1 --texture-width=512 --texture-height=1024 --font-size=35
utils\fontbm\fontbm.exe --font-file fonts\SDKukdetopokki-aLt.otf --output src\generated\fonts\en_shuhun --chars-file src\generated\chars.txt --data-format xml --max-texture-count=1 --texture-width=512 --texture-height=1024 --font-size=35
bin\combine_bitmapfont.exe
copy src\generated\fonts\en_hanyi.fnt assets\bitmapfont\en
copy src\generated\fonts\en_haolong.fnt assets\bitmapfont\en
copy src\generated\fonts\en_shuhun.fnt assets\bitmapfont\en
popd