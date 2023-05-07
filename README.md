# Repubic of Korea GTIN Code

This is a Python module for retrieving product names from the Korean GTIN(Global Trade Item Number) codes.

## Before you begin

Setting up Development Environment for Operating System.

### macOS

To set up the development environment on macOS, open the terminal and execute the following commands:

``` sh
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install pyenv
brew install pyenv

# Install Git
brew install git

# Install Python 3.11.3 using pyenv
pyenv install 3.11.3

# Set the global Python version to 3.11.3
pyenv global 3.11.3

# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate
```

### Windows

To set up the development environment on Windows, open the PowerShell and execute the following commands:

``` sh
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Install Python
choco install python

# Install Git
choco install git

# Create a virtual environment and activate it
python -m venv venv
venv\Scripts\activate.bat
```

### Android
To set up the development environment on Android, open the terminal and execute the following commands:

``` sh
# Install Python
pkg install python

# Install Git
pkg install git

# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate
```

Install the required packages. In the terminal, run the following command:

``` sh
pip install -r requirements.txt
```

## 

## How to use

In your Python script, import the Search class from the gtin module and create a Search object with the GTIN code as the parameter. Then, call the search_gtin() method to retrieve the product name associated with the GTIN code.

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
# Excute Command Line Tool
python main.py

# Excute Tkinter Graphic Tool
python main-gui.py
```

## Result

### Command Line Tool

``` sh
Please enter the GTIN (Product Barcode) number: 8801043056489

GTIN code: 8801043056489
Product name: (주)농심 신라면 건면 사발 77g
```

### Graphic Tool

![Screenshot](/Screenshot.png)

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](/LICENSE) file for details.