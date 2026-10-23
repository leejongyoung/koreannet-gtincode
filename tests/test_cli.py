import io
import json

import pytest

from koreannet_gtin import NotFoundError, Product, cli

GTIN = "8801045759296"
PRODUCT = Product(gtin=GTIN, name="샘플 상품", category="가공식품", manufacturer="(주)샘플")


@pytest.fixture
def fake_lookup(monkeypatch):
    calls = []

    def fake(code, timeout=10.0):
        calls.append(code)
        if code == "8801043056489":
            raise NotFoundError("없음")
        return PRODUCT

    monkeypatch.setattr(cli, "lookup", fake)
    monkeypatch.setattr(cli.time, "sleep", lambda _s: None)
    return calls


def test_bare_number_means_lookup(fake_lookup, capsys):
    assert cli.main([GTIN]) == 0
    out = capsys.readouterr().out
    assert "샘플 상품" in out and "상품명" in out
    assert fake_lookup == [GTIN]


def test_json_single_is_object_and_keeps_hangul(fake_lookup, capsys):
    assert cli.main(["lookup", GTIN, "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["name"] == "샘플 상품"


def test_json_multiple_is_list(fake_lookup, capsys):
    assert cli.main([GTIN, GTIN, "--json"]) == 0
    assert len(json.loads(capsys.readouterr().out)) == 2


def test_partial_failure_exits_1_but_keeps_results(fake_lookup, capsys):
    assert cli.main([GTIN, "8801043056489", "--name-only"]) == 1
    captured = capsys.readouterr()
    assert captured.out.strip() == "샘플 상품"
    assert "8801043056489: 없음" in captured.err


def test_csv_has_header_and_row(fake_lookup, capsys):
    assert cli.main([GTIN, "--csv"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("gtin,name,")
    assert "샘플 상품" in lines[1]


def test_reads_codes_from_file_and_stdin(fake_lookup, tmp_path, monkeypatch, capsys):
    path = tmp_path / "codes.txt"
    path.write_text(f"# 주석\n{GTIN}\n\n", encoding="utf-8")
    monkeypatch.setattr("sys.stdin", io.StringIO(f"{GTIN}\n"))
    assert cli.main(["-", "-f", str(path), "--name-only"]) == 0
    assert fake_lookup == [GTIN, GTIN]


def test_missing_file_is_usage_error(fake_lookup, capsys):
    assert cli.main(["-f", "/no/such/file"]) == 2


def test_no_input_without_tty_is_usage_error(fake_lookup, monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    assert cli.main([]) == 2


def test_check_command_is_offline(capsys):
    assert cli.main(["check", GTIN, "8801045759297"]) == 1
    captured = capsys.readouterr()
    assert f"{GTIN}: OK" in captured.out
    assert "체크디지트" in captured.err
