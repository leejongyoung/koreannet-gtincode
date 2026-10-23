"""코리안넷 GTIN 검색 페이지 조회와 해석."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, fields
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup

from . import __version__
from .errors import NetworkError, NotFoundError, ParseError
from .gtin import normalize

SEARCH_URL = "https://www.koreannet.or.kr/front/koreannet/gtinSrch.do"
DEFAULT_TIMEOUT = 10.0
USER_AGENT = f"koreannet-gtin/{__version__} (+https://github.com/leejongyoung/koreannet-gtincode)"

# 페이지의 항목 이름(th) → Product 필드. 줄바꿈·공백은 비교 전에 제거합니다.
_LABELS = {
    "KAN상품분류코드": "category_code",
    "KAN상품분류": "category",
    "제조국가": "country",
    "제조사/생산자": "manufacturer",
    "판매자": "seller",
    "업체주소(도로명주소)": "address",
    "대표전화": "phone",
    "수정일": "updated",
}

# 사용자에게 보여 줄 한글 이름과 순서.
FIELD_LABELS: Dict[str, str] = {
    "gtin": "바코드(GTIN)",
    "name": "상품명",
    "category": "상품분류",
    "category_code": "분류코드",
    "manufacturer": "제조사",
    "seller": "판매자",
    "country": "제조국가",
    "address": "업체주소",
    "phone": "대표전화",
    "updated": "수정일",
    "image_url": "이미지",
}


@dataclass(frozen=True)
class Product:
    gtin: str
    name: str
    category: Optional[str] = None
    category_code: Optional[str] = None
    manufacturer: Optional[str] = None
    seller: Optional[str] = None
    country: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    updated: Optional[str] = None
    image_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        return asdict(self)

    def rows(self):
        """(한글 항목 이름, 값) 목록. 값이 없는 항목은 뺍니다."""
        data = self.to_dict()
        return [(FIELD_LABELS[f.name], data[f.name]) for f in fields(self) if data[f.name]]


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _label_key(text: str) -> str:
    return re.sub(r"\s+", "", text)


def parse(html: bytes | str, gtin: str) -> Product:
    """검색 결과 HTML에서 상품 정보를 뽑습니다.

    상품이 없으면 `NotFoundError`, 상품 영역은 있는데 상품명이 없으면 `ParseError`.
    """
    soup = BeautifulSoup(html, "html.parser")
    box = soup.select_one("div.good_detail")
    if box is None:
        raise ParseError(
            "검색 결과 영역(div.good_detail)을 찾지 못했습니다. 사이트가 개편되었을 수 있습니다."
        )

    cont = box.select_one("div.cont")
    if cont is None:
        if "검색 결과가 없습니다" in box.get_text():
            raise NotFoundError(f"코리안넷에 등록되지 않은 상품입니다. ({gtin})")
        raise ParseError("상품 영역(div.cont)을 찾지 못했습니다. 사이트가 개편되었을 수 있습니다.")

    name_tag = cont.select_one("div.nm")
    name = _clean(name_tag.get_text()) if name_tag else ""
    if not name:
        raise ParseError("상품명(div.nm)을 찾지 못했습니다. 사이트가 개편되었을 수 있습니다.")

    values: Dict[str, str] = {}
    for field in cont.select("div.field"):
        th, td = field.select_one("div.th"), field.select_one("div.td")
        if th is None or td is None:
            continue
        key = _LABELS.get(_label_key(th.get_text()))
        value = _clean(td.get_text(" "))
        if key and value:
            values[key] = value

    img = box.select_one("div.img_col img")
    image_url = img.get("src") if img is not None else None

    return Product(gtin=gtin, name=name, image_url=image_url or None, **values)


def lookup(
    gtin: str,
    *,
    session: Optional[requests.Session] = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Product:
    """바코드 번호로 코리안넷에서 상품 정보를 조회합니다.

    Raises:
        InvalidGTINError: 번호 형식·체크디지트 오류 (네트워크 요청 전에 발생).
        NotFoundError: 등록된 상품 없음.
        NetworkError: 연결 실패, 시간 초과, HTTP 오류.
        ParseError: 페이지 구조를 해석하지 못함.
    """
    code = normalize(gtin)
    http = session or requests
    try:
        response = http.post(
            SEARCH_URL,
            data={"gtin": code},
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise NetworkError(f"코리안넷에 연결하지 못했습니다: {exc}") from exc
    return parse(response.content, code)
