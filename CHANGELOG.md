# Changelog

## Unreleased

- Docker: `Dockerfile`, `compose.yaml`, multi-arch image published to GHCR on `v*` tags (non-root, read-only friendly, health check).

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
