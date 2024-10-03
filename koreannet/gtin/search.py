import requests
from bs4 import BeautifulSoup

class Search:
    def __init__(self, gtin_num):
        self.gtin = gtin_num if len(gtin_num) == 13 else None
    
    def search_gtin(self):
        if not self.gtin:
            return {
                'gtin_code': None,
                'product_name': None,
                'message': 'GTIN number must be 13 digits.'
            }

        url = "https://www.koreannet.or.kr/front/koreannet/gtinSrch.do"
        params = {'gtin': self.gtin}

        req = requests.post(url, data=params)
        if req.status_code != 200:
            return {
                "gtin_code": self.gtin,
                "product_name": None,
                "message": "Failed to fetch results."
            }

        soup = BeautifulSoup(req.text, 'html.parser')
        product_details = soup.find("div", class_="cont")

        if not product_details:
            return {
                "gtin_code": self.gtin,
                "product_name": None,
                "message": "No search results found."
            }

        product_name = product_details.find("div", class_="nm").text.strip()

        return {
            "gtin_code": self.gtin,
            "product_name": product_name,
            "message": "Success"
        }