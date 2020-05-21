작혼 Plus: 한국어 리소스 팩
========================

![리소스 팩 썸네일](/assets/en/extendRes/emo/e200005/4.png)

작혼 Plus: 한국어 리소스 팩은 [작혼 Plus](https://github.com/MajsoulPlus/majsoul-plus)에서 사용할 수 있는 리소스 팩으로, 다양한 요소를 한국어로 표시합니다.

(현재는 일부 리소스만 한국어로 표시합니다. 이후 다른 리소스의 한국어화 지원이 추가될 수 있습니다.)


### ⚠️ 주의사항 ⚠️

본 리소스 팩을 사용함에 따라 발생하는 모든 문제(예시: 계정 밴, 민사소송)에 대해 저희는 책임을 지지 않습니다.  
당신은 이 리소스 팩을 사용했을 경우 이러한 주의사항을 확인하고 동의한 것입니다.


### 1. 요구사양

- [작혼 Plus](https://github.com/MajsoulPlus/majsoul-plus) Version 2.0.0-beta.8 이상
- 작혼 글로벌 서버 환경(작혼 Plus의 Settings에서 User Data의 Server to play 값을 2로 설정)


### 2. 적용방법

1. 작혼 Plus 런처를 실행하고, 좌측 Resource Packs 메뉴를 선택합니다.
2. 우상단의 폴더 열기 아이콘을 클릭하여 리소스 팩 폴더를 엽니다.
3. [다운로드 링크](https://github.com/yf-dev/majsoul-plus-korean/archive/master.zip)를 클릭하여 `작혼 Plus: 한국어 리소스 팩`을 다운로드합니다.
4. 다운로드한 `작혼 Plus: 한국어 리소스 팩`을 리소스 팩 폴더에 압축 해제합니다.
5. 압축 해제한 폴더의 이름을 `majsoul-plus-korean-master`에서 `korean`으로 변경합니다.
6. 작혼 Plus 런쳐 상단의 새로고침 아이콘을 클릭합니다.
7. 나타난 한국어 리소스 팩을 활성화합니다.


### 3. Asset 갱신

작혼의 버전이 업데이트되어 `ui_en.json` 파일과 `lqc.lqbin` 파일의 구조가 변경될 경우 게임이 정상적으로 구동되지 않을 수 있습니다.

이러한 경우에는 다음과 같은 절차에 따라 파일을 갱신을 시도하세요.  
(현재는 64비트 환경만을 지원합니다.)

1. 작혼 Plus 런처를 실행하고, 좌측 Resource Packs 메뉴를 선택합니다.
2. 우상단의 폴더 열기 아이콘을 클릭하여 리소스 팩 폴더를 엽니다.
3. 열린 리소스 팩 폴더에서 `korean\script` 폴더로 이동합니다.
4. `update_assets.bat` 파일을 실행합니다.
5. 실행한 프로그램이 종료되면, 작혼 Plus 런처에서 Resource Packs 상단의 새로고침 아이콘을 클릭합니다.
6. Launch Game 버튼을 눌러 작혼을 실행하고, 정상적으로 구동되는지 확인합니다.

만약 위 절차를 수행해도 정상적으로 동작하지 않는다면, 본 리소스 팩을 삭제한 후 다시 다운로드 받아 적용하시고 위 절차를 한번 더 수행해보세요.

위 절차를 모두 수행해도 게임이 정상적으로 구동되지 않는다면, 본 리소스 팩이 업데이트 될때까지 기다려주세요!


### 4. 리소스 미리보기

#### 4.1. 스크린샷

![스크린샷 1](/screenshots/1.png)
![스크린샷 2](/screenshots/2.png)
![스크린샷 3](/screenshots/3.png)
![스크린샷 4](/screenshots/4.png)
![스크린샷 5](/screenshots/5.png)

#### 4.2. 이모지

![](/assets/en/extendRes/emo/e200001/1.png)
![](/assets/en/extendRes/emo/e200001/4.png)
![](/assets/en/extendRes/emo/e200002/0.png)
![](/assets/en/extendRes/emo/e200002/7.png)
![](/assets/en/extendRes/emo/e200005/4.png)
![](/assets/en/extendRes/emo/e200006/3.png)
![](/assets/en/extendRes/emo/e200006/5.png)
![](/assets/en/extendRes/emo/e200017/7.png)
![](/assets/en/extendRes/emo/e200018/2.png)
![](/assets/en/extendRes/emo/e200019/0.png)
![](/assets/en/extendRes/emo/e200019/3.png)
![](/assets/en/extendRes/emo/e200020/2.png)


### 5. 개발 가이드

이하의 내용은 리소스 팩을 단순히 사용하는것이 아니라,
실제로 번역을 수정하거나 이 프로젝트를 개발하기 위한 내용입니다.

단순히 리소스 팩을 사용하시려면 `2. 적용방법` 항목을 읽어주세요.

#### 5.1. 요구사양

- Python 3.7 이상
- [Pipenv](https://github.com/pypa/pipenv)

#### 5.2. 라이브러리 다운로드

```
pipenv install --dev
```

#### 5.3. 원본 Asset 병합

```
script\dev\merge_assets.bat
```

병합된 Asset은 `dev-resources\assets-latest`에 저장됩니다.

#### 5.4. lqc.lqbin 파일에서 Sheet 추출

```
script\dev\export_lqc.bat
```

추출된 Sheet는 `src\generated\csv`에 저장됩니다.

#### 5.5. 문장 번역 템플릿 생성

```
script\dev\generate_translation.bat
```

생성된 템플릿은 다음 경로에 저장됩니다.

- `src\generated\translate_sheet_template.csv`
- `src\generated\translate_json_template.csv`

#### 5.6. 문장 번역 작업 진행

먼저 템플릿 파일을 복사하여 번역용 파일 경로에 붙여넣습니다.

아래와 같이 경로와 파일명을 변경하여 붙여넣어주세요.

- `src\generated\translate_sheet_template.csv` => `src\translate_sheet.csv`
- `src\generated\translate_json_template.csv` => `src\translate_json.csv`

복사한 파일을 열어 필요없는 문장(단순 공백, 숫자, 번역하지 않을 문장 등)을 삭제한 후, 적절히 번역하여 저장합니다.

#### 5.7. 이미지 리소스 번역

실제 문자열로 저장되어있지 않은 리소스(이미지 등)는 직접 `dev-resources\assets-latest`에서 복사하여 `assets` 폴더에 경로를 잘 지정하여 붙여넣고 직접 수정합니다.
추후 리소스 수정이 용이하도록 가능하면 작업파일(`.psd` 등)을 같이 보관해주세요.

**새로운 리소스를 번역했다면, `resourcepack.json` 파일에 해당 리소스의 경로를 추가하는 것을 잊지 마세요!**

#### 5.8. 텍스처 아틀라스 번역

리소스 중 파일명이 `.atlas`로 끝나는 파일은 텍스처 아틀라스의 구조 정보를 기록하고 있는 파일입니다.

이 정보를 통해 텍스처 아틀라스의 각 이미지를 분리하고 다시 병합할 수 있습니다.

#### 5.8.1. 텍스처 아틀라스 분해 

먼저, 텍스처 아틀라스를 분해하려면 다음과 같은 명령어를 사용합니다.

(텍스처 아틀라스 파일의 경로가 `.\dev-resources\assets-latest\res\atlas\en\myres.atlas` 일 경우,)

```
pipenv run python .\src\unpack_atlas.py .\dev-resources\assets-latest\res\atlas\en\myres.atlas
```

위 예시와 같이 명령어를 사용하면 `.\dev-resources\assets-latest\res\atlas\en\myres.atlas_unpack` 폴더가 생성되고, 해당 폴더 안에 각 텍스처 이미지가 저장됩니다.

#### 5.8.2. 텍스처 아틀라스 생성 

이제 분해된 텍스처 이미지를 수정하고 다시 패킹하기 위해서는 다음과 같은 명령어를 입력하시면 됩니다.

```
pipenv run python .\src\pack_atlas.py .\dev-resources\assets-latest\res\atlas\en\myres.atlas_unpack
```

(해당 명령어는 기존 `.atlas` 파일과 실제 텍스처 아틀라스 원본 `.png` 파일들을 덮어씌우니 사용하실 때 원본 파일들을 잘 백업해주세요.)

#### 5.8.3. 텍스처 아틀라스 오프셋 지정

`.atlas_unpack` 폴더 내부의 이미지 파일명에 오프셋 정보를 추가하여 `sourceSize`와 `spriteSourceSize` 값을 변경할 수 있습니다.

원본 이미지 파일명이 `filename.png`일 때, 파일명을 `filename[10,-20,0,0].png`과 같이 변경하여 오프셋을 지정합니다.

대괄호 내의 숫자는 각각 다음의 오프셋을 지정합니다.

- spriteSourceSize의 x 오프셋
- spriteSourceSize의 y 오프셋
- sourceSize의 w 오프셋
- sourceSize의 h 오프셋

예를 들어, 원본 이미지 너비를 30px 늘리고(w offset을 -30으로 지정),
우측으로 20px 이동(x offset을 20으로 지정)하고 싶다면 다음과 같이 파일명을 변경합니다.

```
filename[20,0,-30,0].png
```


#### 5.9. 번역 적용

```
script\dev\update_translation.bat
```

#### 5.10. 폰트 갱신

폰트 갱신 작업은 번역 적용(`update_translation.bat`) 과정에 포함되어 있으므로, 번역만을 갱신하기 위해 별도로 실행할 필요는 없습니다.

폰트 파일을 교체했을 경우에만 직접 실행하세요.

```
script\dev\update_font.bat
```

#### 5.11. 사전 빌드 바이너리 갱신

`src` 폴더 내의 파이썬 파일을 수정했을 경우, 사전 빌드 바이너리를 갱신해야 합니다.

```
script\dev\build_src.bat
```


### 6. 일본 서버용 작업

:warning: 일본 서버용 한국어 번역 리소스는 이 프로젝트에서 현재 제공되지 않습니다. :warning:

이하의 내용은 일본 서버에서 한국어 리소스 팩을 만들어 적용하는 방법에 대해서 설명합니다.  
(어느 정도 프로그래밍에 대한 지식이 필요할 수 있습니다)

먼저 본 리소스팩이 있는 폴더에서 명령 프롬프트(powershell 아님)를 실행한 후 다음 명령어를 입력합니다.

```
rmdir .\dev-resources\assets-latest /s /q
cmd /C "set MAJSOUL_LANG=jp&&.\script\merge_assets.bat"
cmd /C "set MAJSOUL_LANG=jp&&.\script\export_lqc.bat"
cmd /C "set MAJSOUL_LANG=jp&&.\script\generate_translation.bat"
```

그 다음 아래 경로의 파일을 복사해 파일명을 변경하여 붙여넣어 주세요.  
(이미 존재하는 파일은 글로벌 서버용이므로 덮어씌워야 합니다)

- `src\generated\translate_sheet_template.csv` => `src\translate_sheet.csv`
- `src\generated\translate_json_template.csv` => `src\translate_json.csv`

복사한 파일을 열어 필요없는 문장(단순 공백, 숫자, 번역하지 않을 문장 등)을 삭제한 후, 적절히 번역하여 저장합니다.

실제 문자열로 저장되어있지 않은 리소스(이미지 등)는 직접 `dev-resources\assets-latest`에서 복사하여 `assets` 폴더에 경로를 잘 지정하여 붙여넣고 직접 수정합니다.
추후 리소스 수정이 용이하도록 가능하면 작업파일(`.psd` 등)을 같이 보관해주세요.

작업이 완료되었으면, 아까와 동일하게 본 리소스팩이 있는 폴더에서 명령 프롬프트(powershell 아님)를 실행한 후 다음 명령어를 입력합니다.

```
cmd /C "set MAJSOUL_LANG=jp&&.\script\update_translation.bat"
```

이후 `resourcepack-jp.json` 파일의 텍스트를 복사하여 `resourcepack.json` 파일에 덮어씌웁니다.

만약 별도로 번역한 리소스(이미지 등)이 있다면, 적절히 `resourcepack.json` 파일에 추가합니다.

이제 작혼 Plus에서 정상적으로 적용이 되었는지 확인하면 작업이 완료됩니다.

(만약, 한글은 출력되지만 한자가 표시되지 않는다면 폰트가 정상적으로 변환되지 않았을 가능성이 높습니다.
이 프로젝트는 배치 스크립트에 대하여 적절한 오류처리를 수행하지 않았으므로, 실제 실행 결과가 명령 프롬프트에 출력되는 것을 확인하면서 오류가 발생한 부분을 찾아야 합니다.)


### Contributors

- [Nesswit](https://github.com/rishubil)
- 신짱구
- 일급천재

이외에도 익명의 기여자분들이 번역에 많은 도움을 주셨습니다. 감사합니다.

### License

MIT

또한, 이 프로젝트는 다음의 제3자 소프트웨어 및 폰트의 바이너리를 포함하고 있습니다.

- [fontbm](https://github.com/vladimirgamalyan/fontbm) - BMFont compatible, cross-platform command line bitmap font generator
- [Protocol Buffers](https://github.com/protocolbuffers/protobuf) - Google's data interchange format
- [Noto Sans (CJK)](https://www.google.com/get/noto/)
- [배달의민족 을지로체](https://www.woowahan.com/#/fonts)
- [산돌국대떡볶이체](http://kukde.co.kr/?page_id=627)
- [정묵 바위체](https://sangsangfont.com/21/?idx=122)