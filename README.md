# koreannet-gtin

[한국어](README.ko.md)

Look up a product by its Korean GTIN (barcode) on [Koreannet](https://www.koreannet.or.kr/) (GS1 Korea / KOREA CHAMBER OF COMMERCE). One package, four ways to use it:

| | |
|---|---|
| **Python library** | `from koreannet_gtin import lookup` |
| **CLI** | `koreannet-gtin 8801045759296` |
| **Desktop GUI** | `koreannet-gtin gui` (tkinter) |
| **Browser UI** | `koreannet-gtin web` (works on phones and servers too) |

Runs on Windows, macOS, Linux and Android (Termux), Python 3.9+.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/web-dark.png">
  <img alt="Browser UI" src="docs/web-light.png" width="520">
</picture>

## Install

```sh
# Recommended: isolated command-line tool
uv tool install git+https://github.com/leejongyoung/koreannet-gtincode
# or
pipx install git+https://github.com/leejongyoung/koreannet-gtincode
```

Prebuilt Windows/macOS/Linux executables (CLI and GUI, no Python needed) are attached to each [release](https://github.com/leejongyoung/koreannet-gtincode/releases).

| Platform | CLI | GUI window | Browser UI |
|---|---|---|---|
| Windows / macOS / Linux | yes | yes | yes |
| Android (Termux) | yes | no tkinter | yes |
| iPhone / iPad | – | – | open the URL of a `web` server running on your PC (`--host 0.0.0.0`) |

Notes: on Linux the GUI needs `python3-tk` (`sudo apt install python3-tk`). On macOS use a Python from python.org, Homebrew or `uv`; the Apple-supplied Python 3.9 ships Tk 8.5, which hangs on recent macOS.

## CLI

```console
$ koreannet-gtin 8801045759296
바코드(GTIN)  8801045759296
상품명        (주)오뚜기 프레스코 베이컨 감자스프 180g
상품분류      가공식품 > 즉석/편의식품 > 즉석/조리식품 > 즉석스프
제조사        (주)오뚜기
...
```

```sh
koreannet-gtin 8801045759296 --json            # JSON (one object, or a list for several codes)
koreannet-gtin 8801045759296 --name-only       # just the product name
koreannet-gtin -f codes.txt --csv > out.csv    # batch from a file ('#' comments allowed)
cat codes.txt | koreannet-gtin - --json        # batch from stdin
koreannet-gtin check 8801045759296             # offline check-digit validation
koreannet-gtin web --port 8765                 # browser UI at http://127.0.0.1:8765/
```

Exit codes: `0` all found, `1` at least one failed, `2` usage error. Batches wait `--delay` seconds (default 1) between requests.

Input is validated before any request: GTIN-8, 12 (UPC-A), 13 (EAN-13) and 14 digits, with GS1 check-digit verification. Spaces and hyphens are ignored.

## Desktop GUI

`koreannet-gtin gui` (or the `koreannet-gtin-gui` launcher / the GUI executable from a release) opens a native tkinter window: type or paste a number, press Enter, and copy the product name or the full JSON. Lookups run in the background, so the window never freezes.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/gui-dark.png">
  <img alt="Desktop GUI (macOS)" src="docs/gui-light.png" width="480">
</picture>

## Python

```python
from koreannet_gtin import lookup, NotFoundError, InvalidGTINError

try:
    product = lookup("8801045759296")
except InvalidGTINError as e:   # bad length or check digit; no request is sent
    ...
except NotFoundError:           # not registered in Koreannet
    ...

print(product.name)             # (주)오뚜기 프레스코 베이컨 감자스프 180g
print(product.manufacturer, product.category, product.to_dict())
```

Errors all derive from `KoreannetError`: `InvalidGTINError`, `NotFoundError`, `NetworkError`, `ParseError` (the page layout changed). `lookup(gtin, session=..., timeout=...)` accepts your own `requests.Session`.

### Migrating from 1.x

`from koreannet.gtin import Search` → `from koreannet_gtin import lookup`. `Search(...).search_gtin()` returned a dict with a `message`; `lookup()` returns a `Product` and raises on failure. `requirements.txt`, `main.py` and `main-gui.py` are replaced by the `koreannet-gtin` command; `pyperclip` is no longer needed.

## About the data

Results come from Koreannet's public search page; this tool does not use an official API. Koreannet's page states that its data is the property of the Korea Chamber of Commerce and that bulk collection and redistribution may be subject to legal action, and its `robots.txt` disallows `/front/koreannet/gtinSrch*` for crawlers. Use this for occasional individual lookups, keep the default batch delay, and do not mirror or redistribute the data. The page layout can change without notice; if it does, `ParseError` is raised instead of wrong data.

## Development

```sh
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest && ruff check . && ruff format --check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md). MIT licensed ([LICENSE](LICENSE)).
