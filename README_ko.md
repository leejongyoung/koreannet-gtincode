# 대한민국 GTIN 코드

이 파이썬 모듈은 대한민국 GTIN(Global Trade Item Number) 코드로부터 제품명을 가져오는 기능을 제공합니다.

## 사용하기 전에

운영체제별로 개발환경을 설정해주세요.

### macOS

macOS에서 개발환경을 설정하기 위해서는 터미널을 열고 다음 명령어를 실행하세요.

``` sh
# Homebrew 설치
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# pyenv 설치
brew install pyenv

# Git 설치
brew install git

# Python 3.11.3 설치
pyenv install 3.11.3

# 전역 Python 버전 설정
pyenv global 3.11.3

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate
```

### Windows

Windows에서 개발환경을 설정하기 위해서는 PowerShell을 열고 다음 명령어를 실행하세요.

``` sh
# Chocolatey 설치
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Python 설치
choco install python

# Git 설치
choco install git

# 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate.bat
```

### Android

Android에서 개발환경을 설정하기 위해서는 터미널을 열고 다음 명령어를 실행하세요.

``` sh
# Python 설치
pkg install python

# Git 설치
pkg install git

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate
```

필요한 패키지를 설치하세요. 터미널에서 다음 명령어를 실행하세요.

``` sh
pip install -r requirements.txt
```

## 사용 방법

Python 스크립트에서 gtin 모듈에서 Search 클래스를 가져오고, GTIN 코드를 매개변수로 해서 Search 객체를 만듭니다. 그런 다음, search_gtin() 메서드를 호출하여 GTIN 코드와 관련된 제품명을 검색하세요.

``` python
from koreannet.gtin import Search

def main():
    gtin_num = input("Please enter the GTIN (Product Barcode) number: ")

    koreannet = Search(gtin_num)
    result = koreannet.search_gtin()

    if result["product_name"]:
        print("GTIN code: " + result["gtin_code"])
        print("Product name: " + result["product_name"])
    else:
        print(result["message"])

if __name__ == "__main__":
    main()
```

``` sh
# 커맨드라인 도구에서 실행
python main.py

# Tkinter 그래픽 도구에서 실행
python main-gui.py
```

## 실행결과

### 커맨드라인 도구

``` sh
Please enter the GTIN (Product Barcode) number: 8801043056489

GTIN code: 8801043056489
Product name: (주)농심 신라면 건면 사발 77g
```

### 그래픽 도구

![스크린샷](/Screenshot.png)

## 라이선스

이 프로젝트는 MIT 라이선스 조건에 따라 라이선스가 부여됩니다. 자세한 내용은 [LICENSE](/LICENSE) 파일을 확인해주세요.