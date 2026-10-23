import json
import threading
import urllib.error
import urllib.request

import pytest

from koreannet_gtin import NetworkError, NotFoundError, Product, web

PRODUCT = Product(gtin="8801045759296", name="샘플 상품")


@pytest.fixture
def server(monkeypatch):
    def fake(code, **_):
        if code == "8801043056489":
            raise NotFoundError("없음")
        if code == "4006381333931":
            raise NetworkError("연결 실패")
        return PRODUCT

    monkeypatch.setattr(web, "lookup", fake)
    httpd = web.make_server("127.0.0.1", 0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def get(url, headers=None):
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def test_index_is_html(server):
    status, body = get(server + "/")
    assert status == 200 and "GTIN 조회".encode() in body


@pytest.mark.parametrize(
    "gtin, status",
    [("8801045759296", 200), ("8801043056489", 404), ("4006381333931", 502)],
)
def test_api_status_mapping(server, gtin, status):
    code, body = get(f"{server}/api/lookup?gtin={gtin}")
    assert code == status
    assert "error" in json.loads(body) or json.loads(body)["name"] == "샘플 상품"


def test_api_invalid_code_is_400(server, monkeypatch):
    monkeypatch.undo()  # 실제 lookup으로 형식 검증만 확인 (네트워크 전에 실패)
    code, body = get(f"{server}/api/lookup?gtin=123")
    assert code == 400 and "error" in json.loads(body)


def test_foreign_host_header_is_rejected_on_loopback(server):
    code, _ = get(server + "/api/lookup?gtin=8801045759296", headers={"Host": "evil.example"})
    assert code == 403


@pytest.mark.parametrize(
    "header, expected",
    [
        ("localhost:8765", "localhost"),
        ("127.0.0.1", "127.0.0.1"),
        ("[::1]:80", "[::1]"),
        ("evil.example:1", "evil.example"),
    ],
)
def test_hostname(header, expected):
    assert web._hostname(header) == expected
