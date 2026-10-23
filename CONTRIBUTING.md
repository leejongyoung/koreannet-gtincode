# Contributing · 기여 안내

1. Fork하고 브랜치를 만듭니다. / Fork the repo and create a branch.
2. `pip install -e ".[dev]"` 후 변경하고 `pytest`, `ruff check .`, `ruff format --check .`가 통과하는지 확인합니다.
3. 동작이 바뀌면 테스트를 추가합니다. 코리안넷 응답을 흉내 내는 HTML은 `tests/fixtures/`에 **직접 만든 최소 예시**로 둡니다(실제 페이지를 통째로 저장하지 않습니다). 테스트에서 실제 사이트에 요청하지 않습니다.
4. 지원 범위는 Python 3.9+ 이고 Windows · macOS · Linux에서 CI가 돕니다. 3.9에서 없는 문법(`match`, `X | Y` 런타임 타입 등)을 쓰지 마세요.
5. PR에 변경 이유와 확인한 방법을 적습니다.

릴리스: `src/koreannet_gtin/__init__.py`의 `__version__`과 `CHANGELOG.md`를 고치고 `vX.Y.Z` 태그를 푸시하면 실행 파일과 wheel이 릴리스에 올라갑니다.
