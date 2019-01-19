# 바코드 크롤러

식품 바코드 데이터를 불러오기 위한 파이썬으로 제작한 크롤러

## 1. 운영체제별 개발환경 설정 방법 (파이썬, git 설치 방법)

터미널을 열고 다음의 명령어를 실행한다.
``` sh
# mac 인 경우 ()
brew install pyenv
brew install git
pyenv install 3.7.2
pyenv global 3.7.2

# windwos의 경우
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
choco install python
choco install git

# android 인 경우
pkg install python
pkg install git
```

## 2. 파이썬 라이브러리 설치

``` sh
pip install -r requirements.txt
```

## 3. 스크립트 실행 방법

``` sh
python main.py
```

## 이 프로젝트 목표

스크립트에서 가져온 이름을 데이터베이스에 연동것이 최종 목표

- [ ] Django로 웹페이지 사이트 호스팅
- [ ] Google Spread Sheet 연동
- [ ] 데이터 베이스 연동

