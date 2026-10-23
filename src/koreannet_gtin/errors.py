"""공개 예외. 모두 `KoreannetError`를 상속합니다."""

from __future__ import annotations


class KoreannetError(Exception):
    """이 패키지가 일으키는 모든 예외의 기반 클래스."""


class InvalidGTINError(KoreannetError, ValueError):
    """바코드 번호 형식이나 체크디지트가 올바르지 않음."""


class NotFoundError(KoreannetError):
    """코리안넷에 등록된 상품이 없음."""


class NetworkError(KoreannetError):
    """코리안넷에 연결하지 못했거나 비정상 응답을 받음."""


class ParseError(KoreannetError):
    """응답은 받았지만 페이지 구조를 해석하지 못함(사이트 개편 가능성)."""
