import pytest

from koreannet_gtin import InvalidGTINError, check_digit, is_valid, normalize


@pytest.mark.parametrize(
    "code", ["8801045759296", "8801043056489", "4006381333931", "036000291452", "96385074"]
)
def test_known_valid_codes(code):
    assert is_valid(code)


def test_check_digit_matches_last_digit():
    assert check_digit("880104575929") == 6


@pytest.mark.parametrize("code", ["8801045759297", "123", "abcdefghijklm", "", "88010457592961"])
def test_invalid_codes(code):
    assert not is_valid(code)


def test_normalize_strips_separators():
    assert normalize(" 880-1045 759296\n") == "8801045759296"


def test_normalize_pads_short_codes_to_13():
    assert normalize("036000291452") == "0036000291452"  # UPC-A
    assert normalize("96385074") == "0000096385074"  # GTIN-8


def test_normalize_strips_leading_zero_of_14_digits():
    assert normalize("08801045759296") == "8801045759296"


def test_normalize_keeps_real_gtin14():
    assert normalize("18801045759293") == "18801045759293"


@pytest.mark.parametrize(
    "raw, fragment",
    [("", "입력하세요"), ("88010457592a6", "숫자만"), ("12345", "자리"), ("8801045759297", "체크디지트")],
)
def test_normalize_errors_are_specific(raw, fragment):
    with pytest.raises(InvalidGTINError, match=fragment):
        normalize(raw)


def test_fullwidth_digits_rejected():
    with pytest.raises(InvalidGTINError):
        normalize("８８０１０４５７５９２９６")
