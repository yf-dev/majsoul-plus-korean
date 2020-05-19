pushd .
cd %~dp0..
setlocal
if not defined MAJSOUL_LANG (
  set MAJSOUL_LANG=en
)
rmdir src\generated\fonts /s /q
mkdir src\generated\fonts
if "%MAJSOUL_LANG%" == "jp" (
  utils\fontbm\fontbm.exe --font-file fonts\NotoSansCJKkr-Medium.otf --output src\generated\fonts\jp_haolong --chars-file src\generated\chars.txt --data-format xml --spacing-vert=1 --spacing-horiz=1 --max-texture-count=1 --texture-width=1536 --texture-height=2096 --font-size=40
  utils\fontbm\fontbm.exe --font-file fonts\NotoSansCJKkr-Medium.otf --output src\generated\fonts\jp_jiye --chars-file src\generated\chars.txt --data-format xml --spacing-vert=1 --spacing-horiz=1 --max-texture-count=1 --texture-width=1024 --texture-height=2096 --font-size=35
) else (
  utils\fontbm\fontbm.exe --font-file fonts\SSRockRegular.ttf --output src\generated\fonts\en_hanyi --chars-file src\generated\chars.txt --data-format xml --spacing-vert=1 --spacing-horiz=1 --max-texture-count=1 --texture-width=512 --texture-height=1024 --font-size=40
  utils\fontbm\fontbm.exe --font-file fonts\BMEULJIROTTF.ttf --output src\generated\fonts\en_haolong --chars-file src\generated\chars.txt --data-format xml --spacing-vert=1 --spacing-horiz=1 --max-texture-count=1 --texture-width=512 --texture-height=1024 --font-size=35
  utils\fontbm\fontbm.exe --font-file fonts\SDKukdetopokki-aLt.otf --output src\generated\fonts\en_shuhun --chars-file src\generated\chars.txt --data-format xml --spacing-vert=1 --spacing-horiz=1 --max-texture-count=1 --texture-width=512 --texture-height=1024 --font-size=35
)
bin\combine_bitmapfont.exe
if "%MAJSOUL_LANG%" == "jp" (
  xcopy /y src\generated\fonts\jp_haolong.fnt assets\bitmapfont\jp\jp_haolong.fnt*
  xcopy /y src\generated\fonts\jp_jiye.fnt assets\bitmapfont\jp\jp_jiye.fnt*
) else (
  xcopy /y src\generated\fonts\en_hanyi.fnt assets\bitmapfont\en\en_hanyi.fnt*
  xcopy /y src\generated\fonts\en_haolong.fnt assets\bitmapfont\en\en_haolong.fnt*
  xcopy /y src\generated\fonts\en_shuhun.fnt assets\bitmapfont\en\en_shuhun.fnt*
)
endlocal
popd