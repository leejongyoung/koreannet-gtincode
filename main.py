#!/usr/bin/env python

import requests
import re
from bs4 import BeautifulSoup

barcode_num = input("바코드 번호 13자리를 입력해주세요: ")

with requests.Session() as s:
    req = s.post("http://www.koreannet.or.kr/home/hpisSrchGtin.gs1?gtin=" + barcode_num)
    if req.status_code == 200:
        soup = BeautifulSoup(req.text, 'html.parser')
        if len(soup.find_all("div", class_="productTit")) != 0:
            for result in soup.find_all("div", class_="productTit"):
                return_msg = re.compile('[\S]+').findall(result.text)
                if return_msg[0] == barcode_num:
                    del return_msg[0]
                    print("바코드: " + barcode_num)
                    print("제품명: " + " ".join(return_msg))
                else:
                    print("바코드 결과값이 일치하지 않습니다")
        else:
            print("지원하지 않는 바코드입니다.\n수동 기입 필요")
    else:
        print("결과를 받아오는데 실패했습니다.")