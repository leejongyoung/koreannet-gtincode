import json
import re
import shutil
import subprocess
import threading
import urllib.error
import urllib.request
from pathlib import Path

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


def test_icon_is_served_as_svg(server):
    status, body = get(server + "/icon.svg")
    assert status == 200 and body.lstrip().startswith(b"<svg")


# ---- 클립보드 대체 경로(보안 컨텍스트가 아닌 LAN HTTP 접속 포함) ----------------------------

HARNESS = Path(__file__).parent / "clipboard_harness.mjs"


def _page_script() -> str:
    from koreannet_gtin import web

    html = web._page().decode("utf-8")
    return re.search(r"<script>(.*?)</script>", html, re.S).group(1)


def _run_page(secure: bool, clipboard: str) -> dict:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node 가 없어 페이지 스크립트를 실행할 수 없습니다")
    payload = json.dumps({"script": _page_script(), "secure": secure, "clipboard": clipboard})
    # Windows 의 기본 코드 페이지(cp1252)로 한글이 깨지지 않도록 바이트로 주고받는다.
    done = subprocess.run([node, str(HARNESS)], input=payload.encode("utf-8"), capture_output=True, timeout=30)
    assert done.returncode == 0, done.stderr.decode("utf-8", "replace")
    return json.loads(done.stdout.decode("utf-8"))


def test_insecure_context_shows_selectable_text_instead_of_a_silent_failure():
    # LAN HTTP: window.isSecureContext 가 false 이고 navigator.clipboard 가 없다.
    r = _run_page(secure=False, clipboard="none")
    assert r["afterJson"]["manualHidden"] is False
    assert r["afterJson"]["area"] == r["jsonText"], "JSON 전체가 선택 가능한 텍스트로 나와야 한다"
    assert r["afterJson"]["writes"] == []
    assert r["afterJson"]["msgClass"] == "error" and "직접 복사" in r["afterJson"]["msg"]
    assert r["afterName"]["writes"] == []
    assert r["pasteDisabled"] is True and "직접 붙여넣기" in r["pastePlaceholder"]


def test_secure_context_copies_with_the_clipboard_api():
    r = _run_page(secure=True, clipboard="ok")
    assert r["afterJson"]["writes"] == [r["jsonText"]]
    assert r["afterJson"]["manualHidden"] is True and r["afterJson"]["msg"] == "복사했습니다."
    assert r["afterName"]["writes"][-1] == "테스트 상품"
    assert r["pasteDisabled"] is False


def test_clipboard_permission_denied_falls_back_to_manual_copy():
    r = _run_page(secure=True, clipboard="deny")
    assert r["afterJson"]["manualHidden"] is False
    assert r["afterJson"]["area"] == r["jsonText"]
    assert r["afterJson"]["writes"] == []
