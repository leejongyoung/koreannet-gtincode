import requests
import re
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

        url = "http://www.koreannet.or.kr/home/hpisSrchGtin.gs1"
        params = {'gtin': self.gtin}
        
        req = requests.post(url, data=params)
        if req.status_code != 200:
            return {
                "gtin_code": self.gtin,
                "product_name": None,
                "message": "Failed to fetch results."
            }
        
        soup = BeautifulSoup(req.text, 'html.parser')
        product_titles = soup.find_all("div", class_="productTit")
        if not product_titles:
            return {
                "gtin_code": self.gtin,
                "product_name": None,
                "message": "No search results found."
            }

        for result in product_titles:
            return_msg = re.findall(r'\S+', result.text)
            if return_msg[0] == self.gtin:
                del return_msg[0]
                return {
                    "gtin_code": self.gtin,
                    "product_name": " ".join(return_msg)
                }
