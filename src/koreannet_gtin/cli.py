"""명령줄 인터페이스: `koreannet-gtin`."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
import unicodedata
from typing import Iterable, List, Optional, Sequence, TextIO

from . import __version__
from .client import DEFAULT_TIMEOUT, FIELD_LABELS, Product, lookup
from .errors import InvalidGTINError, KoreannetError
from .gtin import normalize

SUBCOMMANDS = {"lookup", "check", "gui", "web"}
EXIT_OK, EXIT_FAILED, EXIT_USAGE = 0, 1, 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="koreannet-gtin",
        description="바코드(GTIN) 번호로 코리안넷에서 상품 정보를 조회합니다.",
        epilog="하위 명령 없이 번호만 주면 lookup으로 동작합니다. 예: koreannet-gtin 8801045759296",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="{lookup,check,gui,web}")

    p = sub.add_parser("lookup", help="상품 정보 조회 (기본)")
    p.add_argument("gtin", nargs="*", help="바코드 번호. 여러 개 가능, '-'는 표준 입력")
    p.add_argument("-f", "--file", metavar="PATH", help="줄마다 번호가 적힌 파일")
    fmt = p.add_mutually_exclusive_group()
    fmt.add_argument("--json", action="store_true", help="JSON으로 출력")
    fmt.add_argument("--csv", action="store_true", help="CSV로 출력")
    fmt.add_argument("--name-only", action="store_true", help="상품명만 출력")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="요청 제한 시간(초)")
    p.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="여러 개를 조회할 때 요청 사이 대기(초, 기본 1.0). 서버 부담을 줄입니다.",
    )

    p = sub.add_parser("check", help="체크디지트만 검사 (네트워크 사용 안 함)")
    p.add_argument("gtin", nargs="+", help="바코드 번호")

    sub.add_parser("gui", help="데스크톱 창(tkinter) 실행")

    p = sub.add_parser("web", help="브라우저용 화면을 로컬 서버로 실행")
    p.add_argument("--host", default="127.0.0.1", help="바인딩 주소 (기본 127.0.0.1)")
    p.add_argument("--port", type=int, default=8765, help="포트 (기본 8765, 0이면 빈 포트)")
    p.add_argument("--no-browser", action="store_true", help="브라우저를 자동으로 열지 않음")
    return parser


def _collect_codes(args: argparse.Namespace, stdin: TextIO) -> List[str]:
    codes: List[str] = []
    for item in args.gtin:
        if item == "-":
            codes.extend(stdin.read().split())
        else:
            codes.append(item)
    if args.file:
        with open(args.file, encoding="utf-8-sig") as handle:
            codes.extend(line.strip() for line in handle if line.strip() and not line.startswith("#"))
    return codes


def _display_width(text: str) -> int:
    # 한글·전각 문자는 터미널에서 2칸을 차지합니다.
    return sum(2 if unicodedata.east_asian_width(char) in "WF" else 1 for char in text)


def _format_text(product: Product) -> str:
    rows = product.rows()
    width = max(_display_width(label) for label, _ in rows)
    return "\n".join(f"{label}{' ' * (width - _display_width(label))}  {value}" for label, value in rows)


def _run_lookup(args: argparse.Namespace, stdin: TextIO, out: TextIO, err: TextIO) -> int:
    try:
        codes = _collect_codes(args, stdin)
    except OSError as exc:
        print(f"파일을 읽지 못했습니다: {exc}", file=err)
        return EXIT_USAGE
    if not codes:
        if stdin.isatty() and not args.file:
            try:
                codes = [input("바코드(GTIN) 번호를 입력하세요: ")]
            except EOFError:
                return EXIT_USAGE
        else:
            print("조회할 번호가 없습니다. `koreannet-gtin --help`를 보세요.", file=err)
            return EXIT_USAGE

    products: List[Product] = []
    failures = 0
    for index, code in enumerate(codes):
        if index and args.delay > 0:
            time.sleep(args.delay)
        try:
            products.append(lookup(code, timeout=args.timeout))
        except KoreannetError as exc:
            failures += 1
            print(f"{code}: {exc}", file=err)
        else:
            if not (args.json or args.csv):
                if args.name_only:
                    print(products[-1].name, file=out)
                else:
                    if len(products) > 1:
                        print(file=out)
                    print(_format_text(products[-1]), file=out)

    if args.json:
        payload = [p.to_dict() for p in products]
        json.dump(payload[0] if len(codes) == 1 and payload else payload, out, ensure_ascii=False, indent=2)
        print(file=out)
    elif args.csv:
        _write_csv(products, out)
    return EXIT_FAILED if failures else EXIT_OK


def _write_csv(products: Iterable[Product], out: TextIO) -> None:
    writer = csv.DictWriter(out, fieldnames=list(FIELD_LABELS), lineterminator="\n")
    writer.writeheader()
    for product in products:
        writer.writerow(product.to_dict())


def _run_check(args: argparse.Namespace, out: TextIO, err: TextIO) -> int:
    bad = 0
    for code in args.gtin:
        try:
            print(f"{code}: OK ({normalize(code)})", file=out)
        except InvalidGTINError as exc:
            bad += 1
            print(f"{code}: {exc}", file=err)
    return EXIT_FAILED if bad else EXIT_OK


def _configure_streams() -> None:
    # Windows 콘솔의 기본 코드페이지(cp949 등)에서도 한글이 깨지지 않게 합니다.
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")


def main(argv: Optional[Sequence[str]] = None) -> int:
    _configure_streams()
    args_list = list(sys.argv[1:] if argv is None else argv)
    # 하위 명령 없이 번호·옵션만 오면 lookup으로 처리.
    if args_list and args_list[0] not in SUBCOMMANDS and args_list[0] not in {"-h", "--help", "--version"}:
        args_list.insert(0, "lookup")
    parser = build_parser()
    args = parser.parse_args(args_list)

    if args.command is None:
        args = parser.parse_args(["lookup"])
    if args.command == "lookup":
        return _run_lookup(args, sys.stdin, sys.stdout, sys.stderr)
    if args.command == "check":
        return _run_check(args, sys.stdout, sys.stderr)
    if args.command == "gui":
        from .gui import main as gui_main

        return gui_main()
    if args.command == "web":
        from .web import serve

        return serve(args.host, args.port, open_browser=not args.no_browser)
    parser.error(f"알 수 없는 명령: {args.command}")
    return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
