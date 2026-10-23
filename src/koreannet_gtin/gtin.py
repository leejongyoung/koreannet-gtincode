"""GTIN(바코드 번호) 정규화와 체크디지트 검증. 네트워크를 쓰지 않습니다."""

from __future__ import annotations

import re

from .errors import InvalidGTINError

_VALID_LENGTHS = (8, 12, 13, 14)
_SEPARATORS = re.compile(r"[\s\-]")


def check_digit(body: str) -> int:
    """체크디지트를 뺀 숫자열 `body`의 GS1 mod-10 체크디지트를 구합니다."""
    if not body.isdigit():
        raise ValueError("body must contain digits only")
    total = 0
    # 오른쪽(체크디지트 바로 왼쪽)부터 가중치 3, 1, 3, 1 ...
    for index, char in enumerate(reversed(body)):
        total += int(char) * (3 if index % 2 == 0 else 1)
    return (10 - total % 10) % 10


def is_valid(gtin: str) -> bool:
    """8·12·13·14자리 GTIN이고 체크디지트가 맞으면 True."""
    if not (gtin.isascii() and gtin.isdigit()) or len(gtin) not in _VALID_LENGTHS:
        return False
    return check_digit(gtin[:-1]) == int(gtin[-1])


def normalize(raw: str) -> str:
    """입력을 검증하고 코리안넷이 받는 13자리로 맞춥니다.

    공백·하이픈은 제거합니다. 8자리(GTIN-8)와 12자리(UPC-A)는 앞에 0을 채워 13자리로,
    앞자리가 0인 14자리는 그 0을 떼어 13자리로 만듭니다. 앞자리가 0이 아닌 14자리
    (GTIN-14)는 그대로 둡니다.
    """
    cleaned = _SEPARATORS.sub("", raw or "")
    if not cleaned:
        raise InvalidGTINError("바코드 번호를 입력하세요.")
    if not (cleaned.isascii() and cleaned.isdigit()):
        raise InvalidGTINError("바코드 번호는 숫자만 입력할 수 있습니다.")
    if len(cleaned) not in _VALID_LENGTHS:
        raise InvalidGTINError(f"바코드 번호는 8, 12, 13, 14자리여야 합니다. (입력: {len(cleaned)}자리)")
    if check_digit(cleaned[:-1]) != int(cleaned[-1]):
        raise InvalidGTINError(
            f"체크디지트가 맞지 않습니다. 마지막 숫자는 {check_digit(cleaned[:-1])}이어야 합니다."
        )
    if len(cleaned) < 13:
        return cleaned.zfill(13)
    if len(cleaned) == 14 and cleaned[0] == "0":
        return cleaned[1:]
    return cleaned
