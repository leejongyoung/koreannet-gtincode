# /// script
# requires-python = ">=3.9"
# dependencies = ["pillow"]
# ///
"""assets/icon.svg 에서 플랫폼별 아이콘을 만듭니다.  실행: uv run packaging/make_icons.py

1. Chrome으로 SVG → assets/icon-1024.png (투명 배경)를 렌더링합니다. Chrome이 없으면 기존 PNG를 씁니다.
2. macOS: assets/icon.icns (iconutil 필요, macOS에서만)
3. Windows: assets/icon.ico
4. 창 아이콘·웹 파비콘용으로 src/koreannet_gtin/_icon.py 를 생성합니다.
"""

from __future__ import annotations

import base64
import io
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SVG = ASSETS / "icon.svg"
PNG = ASSETS / "icon-1024.png"
CHROME_CANDIDATES = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chrome") or "",
]


def render_png() -> None:
    chrome = next((c for c in CHROME_CANDIDATES if c and Path(c).exists()), None)
    if not chrome:
        print("Chrome을 찾지 못해 기존 icon-1024.png를 사용합니다.")
        return
    with tempfile.TemporaryDirectory() as profile:
        PNG.unlink(missing_ok=True)
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                "--default-background-color=00000000",
                "--window-size=1024,1024",
                f"--user-data-dir={profile}",
                f"--screenshot={PNG}",
                SVG.as_uri(),
            ],
            check=True,
            capture_output=True,
        )


def make_icns(base: Image.Image) -> None:
    if sys.platform != "darwin" or not shutil.which("iconutil"):
        print("macOS가 아니라 icon.icns는 건너뜁니다.")
        return
    with tempfile.TemporaryDirectory() as tmp:
        iconset = Path(tmp) / "icon.iconset"
        iconset.mkdir()
        for size in (16, 32, 128, 256, 512):
            base.resize((size, size), Image.LANCZOS).save(iconset / f"icon_{size}x{size}.png")
            base.resize((size * 2, size * 2), Image.LANCZOS).save(iconset / f"icon_{size}x{size}@2x.png")
        subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(ASSETS / "icon.icns")], check=True)


def make_ico(base: Image.Image) -> None:
    # Windows는 여백 없이 꽉 찬 아이콘이 보기 좋으므로 투명 여백을 잘라냅니다.
    cropped = base.crop(base.getbbox())
    cropped.save(ASSETS / "icon.ico", sizes=[(s, s) for s in (16, 24, 32, 48, 64, 128, 256)])


def make_module(base: Image.Image) -> None:
    cropped = base.crop(base.getbbox()).resize((256, 256), Image.LANCZOS)
    buffer = io.BytesIO()
    cropped.save(buffer, "PNG", optimize=True)
    b64 = base64.b64encode(buffer.getvalue()).decode()
    svg = SVG.read_text(encoding="utf-8").strip()
    lines = [b64[i : i + 100] for i in range(0, len(b64), 100)]
    body = "\n".join(f'    "{line}"' for line in lines)
    (ROOT / "src" / "koreannet_gtin" / "_icon.py").write_text(
        '"""앱 아이콘. packaging/make_icons.py 가 생성하므로 직접 고치지 마세요."""\n\n'
        f"ICON_PNG_B64 = (\n{body}\n)\n\n"
        f"ICON_SVG = {svg!r}\n",
        encoding="utf-8",
    )


def main() -> None:
    render_png()
    base = Image.open(PNG).convert("RGBA")
    make_icns(base)
    make_ico(base)
    make_module(base)
    print("done:", ", ".join(sorted(p.name for p in ASSETS.iterdir())))


if __name__ == "__main__":
    main()
