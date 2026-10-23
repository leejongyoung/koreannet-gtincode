# Changelog

## 2.1.1

- No code changes. Re-release so the `2.1.1`/`latest` Docker tags are published once the GHCR package is public.

## 2.1.0

- Docker: `Dockerfile`, `compose.yaml`, and a multi-arch (amd64/arm64) image published to `ghcr.io/leejongyoung/koreannet-gtincode` on `v*` tags (non-root, read-only friendly, health check).
- Repository is public; README badges are live (CI, release, downloads, license).

## 2.0.0

Breaking: new package name and API. See "Migrating from 1.x" in the README.

- `pip`-installable package `koreannet-gtin` (src layout, `pyproject.toml`); import `koreannet_gtin`.
- `lookup()` returns a `Product` (name, category, manufacturer, seller, country, address, phone, updated, image URL) and raises typed errors instead of returning a `message` dict.
- GTIN validation before any request: GTIN-8/12/13/14 and GS1 check digit.
- `koreannet-gtin` CLI: text / JSON / CSV output, batch via file or stdin with throttling, offline `check`, meaningful exit codes.
- tkinter GUI rewritten: non-blocking lookups, history, clipboard helpers, full result table; no `pyperclip` dependency.
- Browser UI (`koreannet-gtin web`) using only the standard library; loopback-only by default with Host-header check.
- Request timeout and an identifying User-Agent.
- Tests, CI on Windows/macOS/Linux × Python 3.9–3.13, release workflow that builds standalone executables.
