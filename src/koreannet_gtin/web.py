"""브라우저용 화면. 표준 라이브러리 HTTP 서버로 동작하므로 추가 설치가 필요 없습니다.

tkinter가 없는 환경(Android Termux, 서버, 일부 Linux)이나 휴대폰 브라우저에서 쓸 수 있습니다.
"""

from __future__ import annotations

import json
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, Tuple
from urllib.parse import parse_qs, urlsplit

from . import __version__
from ._icon import ICON_SVG
from .client import FIELD_LABELS, lookup
from .errors import InvalidGTINError, NetworkError, NotFoundError, ParseError

_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "[::1]", "::1"}

PAGE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GTIN 조회 · 코리안넷</title>
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<style>
  :root { color-scheme: light dark; --accent: #2563eb; --border: #8884; }
  * { box-sizing: border-box; }
  body { margin: 0; font: 16px/1.5 system-ui, -apple-system, "Segoe UI", "Noto Sans KR", sans-serif; }
  main { max-width: 640px; margin: 0 auto; padding: 32px 16px 64px; }
  h1 { font-size: 1.4rem; margin: 0 0 4px; display: flex; align-items: center; gap: 10px; }
  h1 img { width: 40px; height: 40px; }
  p.sub { margin: 0 0 24px; opacity: .7; }
  form { display: flex; gap: 8px; }
  input { flex: 1; min-width: 0; padding: 12px 14px; font: inherit; letter-spacing: .05em;
          border: 1px solid var(--border); border-radius: 10px; background: transparent; color: inherit; }
  input:focus { outline: 2px solid var(--accent); border-color: transparent; }
  button { padding: 12px 18px; font: inherit; border: 0; border-radius: 10px; cursor: pointer;
           background: var(--accent); color: #fff; }
  button.ghost { background: transparent; color: inherit; border: 1px solid var(--border); }
  button:disabled { opacity: .5; cursor: default; }
  #msg { margin: 16px 0; min-height: 1.5em; }
  #msg.error { color: #dc2626; }
  .card { border: 1px solid var(--border); border-radius: 14px; padding: 20px; }
  .card h2 { font-size: 1.2rem; margin: 0 0 12px; word-break: keep-all; }
  dl { display: grid; grid-template-columns: max-content 1fr; gap: 6px 16px; margin: 0; }
  dt { opacity: .6; }
  dd { margin: 0; word-break: break-word; }
  .actions { display: flex; gap: 8px; margin-top: 16px; }
  img { max-width: 160px; border-radius: 8px; margin-bottom: 12px; display: block; }
  footer { margin-top: 32px; font-size: .8rem; opacity: .6; }
</style>
</head>
<body>
<main>
  <h1><img src="/icon.svg" alt="">GTIN 조회</h1>
  <p class="sub">바코드 번호로 코리안넷의 상품 정보를 찾습니다.</p>
  <form id="f">
    <input id="q" inputmode="numeric" autocomplete="off" autofocus placeholder="8801045759296" aria-label="바코드 번호">
    <button class="ghost" type="button" id="paste">붙여넣기</button>
    <button type="submit" id="go">조회</button>
  </form>
  <div id="msg" role="status"></div>
  <div id="out"></div>
  <footer>koreannet-gtin __VERSION__ · 데이터 출처: 대한상공회의소 유통물류진흥원 코리안넷</footer>
</main>
<script>
const FIELDS = __FIELDS__;
const $ = (id) => document.getElementById(id);
let current = null;

function show(msg, isError) { const m = $("msg"); m.textContent = msg || ""; m.className = isError ? "error" : ""; }

function render(p) {
  current = p;
  const out = $("out"); out.replaceChildren();
  const card = document.createElement("div"); card.className = "card";
  if (p.image_url) {
    const img = document.createElement("img"); img.alt = ""; img.referrerPolicy = "no-referrer"; img.src = p.image_url;
    img.onerror = () => img.remove(); card.append(img);
  }
  const h = document.createElement("h2"); h.textContent = p.name; card.append(h);
  const dl = document.createElement("dl");
  for (const [key, label] of FIELDS) {
    if (key === "name" || key === "image_url" || !p[key]) continue;
    const dt = document.createElement("dt"); dt.textContent = label;
    const dd = document.createElement("dd"); dd.textContent = p[key];
    dl.append(dt, dd);
  }
  card.append(dl);
  const actions = document.createElement("div"); actions.className = "actions";
  for (const [text, fn] of [["상품명 복사", () => p.name], ["JSON 복사", () => JSON.stringify(p, null, 2)]]) {
    const b = document.createElement("button"); b.className = "ghost"; b.type = "button"; b.textContent = text;
    b.onclick = async () => { try { await navigator.clipboard.writeText(fn()); show("복사했습니다."); } catch { show("복사하지 못했습니다.", true); } };
    actions.append(b);
  }
  card.append(actions); out.append(card);
}

$("f").addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = $("q").value.trim();
  if (!q) return show("바코드 번호를 입력하세요.", true);
  $("go").disabled = true; show("조회 중…"); $("out").replaceChildren();
  try {
    const res = await fetch("/api/lookup?gtin=" + encodeURIComponent(q));
    const data = await res.json();
    if (res.ok) { show(""); render(data); } else { show(data.error, true); }
  } catch { show("서버에 연결하지 못했습니다.", true); }
  finally { $("go").disabled = false; }
});

$("paste").addEventListener("click", async () => {
  try { $("q").value = (await navigator.clipboard.readText()).trim(); $("q").focus(); }
  catch { show("클립보드를 읽지 못했습니다. 직접 붙여넣어 주세요.", true); }
});
</script>
</body>
</html>
"""


def _page() -> bytes:
    fields = json.dumps([[k, v] for k, v in FIELD_LABELS.items()], ensure_ascii=False)
    return PAGE.replace("__FIELDS__", fields).replace("__VERSION__", __version__).encode("utf-8")


def api_lookup(gtin: str) -> Tuple[int, Dict[str, object]]:
    """`/api/lookup` 본체. (HTTP 상태, JSON 본문)을 돌려줍니다."""
    try:
        return HTTPStatus.OK, lookup(gtin).to_dict()
    except InvalidGTINError as exc:
        return HTTPStatus.BAD_REQUEST, {"error": str(exc)}
    except NotFoundError as exc:
        return HTTPStatus.NOT_FOUND, {"error": str(exc)}
    except (NetworkError, ParseError) as exc:
        return HTTPStatus.BAD_GATEWAY, {"error": str(exc)}


def _hostname(header: str) -> str:
    """Host 헤더에서 포트를 뗀 호스트 이름. IPv6는 대괄호를 유지합니다."""
    if header.startswith("["):
        return header.split("]", 1)[0] + "]"
    return header.rsplit(":", 1)[0] if ":" in header else header


class Handler(BaseHTTPRequestHandler):
    server_version = f"koreannet-gtin/{__version__}"

    def _host_allowed(self) -> bool:
        # 루프백에만 바인딩했을 때는 Host 헤더를 검사해 DNS 리바인딩으로
        # 다른 사이트가 이 서버를 호출하지 못하게 합니다.
        if not getattr(self.server, "loopback_only", True):
            return True
        return _hostname(self.headers.get("Host") or "") in _LOOPBACK_HOSTS

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        if not self._host_allowed():
            return self._send(HTTPStatus.FORBIDDEN, b"forbidden", "text/plain; charset=utf-8")
        url = urlsplit(self.path)
        if url.path == "/":
            return self._send(HTTPStatus.OK, _page(), "text/html; charset=utf-8")
        if url.path == "/icon.svg":
            return self._send(HTTPStatus.OK, ICON_SVG.encode("utf-8"), "image/svg+xml")
        if url.path == "/api/lookup":
            gtin = (parse_qs(url.query).get("gtin") or [""])[0]
            status, payload = api_lookup(gtin)
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            return self._send(status, body, "application/json; charset=utf-8")
        self._send(HTTPStatus.NOT_FOUND, b"not found", "text/plain; charset=utf-8")

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        pass


def make_server(host: str = "127.0.0.1", port: int = 8765) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), Handler)
    server.daemon_threads = True
    server.loopback_only = host in _LOOPBACK_HOSTS  # type: ignore[attr-defined]
    return server


def serve(host: str = "127.0.0.1", port: int = 8765, *, open_browser: bool = True) -> int:
    try:
        server = make_server(host, port)
    except OSError as exc:
        print(f"서버를 시작하지 못했습니다: {exc}")
        return 1
    shown_host = "127.0.0.1" if host in ("", "0.0.0.0", "::") else host
    url = f"http://{shown_host}:{server.server_address[1]}/"
    print(f"GTIN 조회 화면: {url}  (종료: Ctrl+C)")
    if open_browser:
        threading.Timer(0.3, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
    return 0
