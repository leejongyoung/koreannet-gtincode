from pathlib import Path

import pytest
import requests

from koreannet_gtin import (
    InvalidGTINError,
    NetworkError,
    NotFoundError,
    ParseError,
    lookup,
    parse,
)
from koreannet_gtin.client import SEARCH_URL

FIXTURES = Path(__file__).parent / "fixtures"
GTIN = "8801045759296"


def fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


class FakeSession:
    def __init__(self, body=b"", status=200, error=None):
        self.body, self.status, self.error = body, status, error
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.error:
            raise self.error
        response = requests.Response()
        response.status_code = self.status
        response._content = self.body
        response.url = url
        return response


def test_parse_extracts_all_known_fields():
    product = parse(fixture("found.html"), GTIN)
    assert product.name == "(주)샘플 테스트 상품 180g"
    assert product.category == "가공식품 > 즉석스프"
    assert product.category_code == "01120103"
    assert product.country == "KOREA, REPUBLIC OF"
    assert product.manufacturer == "(주)샘플"
    assert product.seller == "(주)샘플"
    assert product.address == "경기 안양시 평촌동 160-4 (경기 안양시 흥안대로 405)"
    assert product.phone == "02-0000-0000"
    assert product.updated == "2023-04-18 13:55:27"
    assert product.image_url == "http://example.test/p.jpg"


def test_parse_ignores_commented_out_markup_and_unknown_fields():
    product = parse(fixture("found.html"), GTIN)
    assert "주석" not in product.name
    assert "무시됨" not in product.to_dict().values()


def test_product_rows_skip_empty_values():
    product = parse(fixture("found.html"), GTIN)
    labels = [label for label, _ in product.rows()]
    assert labels[:2] == ["바코드(GTIN)", "상품명"]


def test_parse_not_found():
    with pytest.raises(NotFoundError):
        parse(fixture("not_found.html"), GTIN)


def test_parse_unknown_layout_is_not_reported_as_not_found():
    with pytest.raises(ParseError):
        parse(fixture("redesigned.html"), GTIN)


def test_lookup_posts_normalized_code_with_user_agent_and_timeout():
    session = FakeSession(fixture("found.html"))
    product = lookup("880-1045-759296", session=session, timeout=3)
    ((url, kwargs),) = session.calls
    assert url == SEARCH_URL
    assert kwargs["data"] == {"gtin": GTIN}
    assert kwargs["timeout"] == 3
    assert kwargs["headers"]["User-Agent"].startswith("koreannet-gtin/")
    assert product.gtin == GTIN


def test_lookup_rejects_bad_code_without_network():
    session = FakeSession(fixture("found.html"))
    with pytest.raises(InvalidGTINError):
        lookup("8801045759297", session=session)
    assert session.calls == []


def test_lookup_wraps_http_and_connection_errors():
    with pytest.raises(NetworkError):
        lookup(GTIN, session=FakeSession(b"", status=503))
    with pytest.raises(NetworkError):
        lookup(GTIN, session=FakeSession(error=requests.ConnectTimeout("slow")))
