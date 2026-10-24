#!/bin/sh
# koreannet-gtin 설치 스크립트 (macOS · Linux)
#
#   curl -fsSL https://raw.githubusercontent.com/leejongyoung/koreannet-gtincode/main/install.sh | sh
#
# 릴리스의 실행 파일을 SHA256SUMS로 검증한 뒤 설치합니다.
#   CLI : ~/.local/bin/koreannet-gtin            (KOREANNET_GTIN_BIN_DIR로 변경)
#   GUI : macOS  ~/Applications/koreannet-gtin-gui.app (KOREANNET_GTIN_APP_DIR로 변경)
#         Linux  ~/.local/bin/koreannet-gtin-gui
# curl로 받은 파일에는 macOS 격리(quarantine) 속성이 붙지 않아 xattr나 "열기" 없이 바로 실행됩니다.
#
# 옵션: --no-gui  GUI를 설치하지 않음 / 환경변수 KOREANNET_GTIN_VERSION=v2.2.0  특정 버전
set -eu

REPO="leejongyoung/koreannet-gtincode"
VERSION="${KOREANNET_GTIN_VERSION:-latest}"
BIN_DIR="${KOREANNET_GTIN_BIN_DIR:-$HOME/.local/bin}"
APP_DIR="${KOREANNET_GTIN_APP_DIR:-$HOME/Applications}"
WITH_GUI=1
for arg in "$@"; do
  case "$arg" in
    --no-gui) WITH_GUI=0 ;;
    -h|--help)
      echo "사용법: install.sh [--no-gui]"
      echo "환경변수: KOREANNET_GTIN_VERSION(예: v2.2.0), KOREANNET_GTIN_BIN_DIR, KOREANNET_GTIN_APP_DIR"
      exit 0 ;;
    *) echo "알 수 없는 옵션: $arg" >&2; exit 2 ;;
  esac
done

die() { echo "오류: $*" >&2; exit 1; }
command -v curl >/dev/null 2>&1 || die "curl이 필요합니다."

os="$(uname -s)"; arch="$(uname -m)"
case "$os/$arch" in
  Darwin/arm64)            platform="macos-arm64" ;;
  Darwin/x86_64)           platform="macos-x64" ;;
  Linux/x86_64|Linux/amd64) platform="linux-x64" ;;
  *) die "지원하지 않는 플랫폼입니다: $os/$arch (pip/uv/Docker로 설치할 수 있습니다)" ;;
esac

if [ -n "${KOREANNET_GTIN_BASE_URL:-}" ]; then
  base="$KOREANNET_GTIN_BASE_URL"   # 미러·테스트용
elif [ "$VERSION" = "latest" ]; then
  base="https://github.com/$REPO/releases/latest/download"
else
  base="https://github.com/$REPO/releases/download/$VERSION"
fi

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT INT TERM

sha256() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -d' ' -f1
  else shasum -a 256 "$1" | cut -d' ' -f1; fi
}

fetch() { # 이름 -> $tmp/이름, 체크섬 검증
  name="$1"
  echo "내려받는 중: $name"
  curl -fsSL "$base/$name" -o "$tmp/$name" || die "$name 을(를) 받지 못했습니다. (버전: $VERSION)"
  expected="$(grep "  $name\$" "$tmp/SHA256SUMS" | cut -d' ' -f1 || true)"
  [ -n "$expected" ] || die "SHA256SUMS에 $name 항목이 없습니다."
  [ "$(sha256 "$tmp/$name")" = "$expected" ] || die "$name 체크섬이 일치하지 않습니다. 설치를 중단합니다."
}

curl -fsSL "$base/SHA256SUMS" -o "$tmp/SHA256SUMS" || die "SHA256SUMS를 받지 못했습니다. 이 버전은 설치 스크립트를 지원하지 않을 수 있습니다."

mkdir -p "$BIN_DIR"
fetch "koreannet-gtin-$platform"
install -m 755 "$tmp/koreannet-gtin-$platform" "$BIN_DIR/koreannet-gtin"
echo "설치됨: $BIN_DIR/koreannet-gtin"

if [ "$WITH_GUI" = 1 ]; then
  case "$os" in
    Darwin)
      command -v unzip >/dev/null 2>&1 || die "unzip이 필요합니다."
      fetch "koreannet-gtin-gui-$platform.zip"
      mkdir -p "$APP_DIR"
      rm -rf "$APP_DIR/koreannet-gtin-gui.app"
      unzip -q "$tmp/koreannet-gtin-gui-$platform.zip" -d "$APP_DIR"
      echo "설치됨: $APP_DIR/koreannet-gtin-gui.app"
      ;;
    Linux)
      fetch "koreannet-gtin-gui-$platform"
      install -m 755 "$tmp/koreannet-gtin-gui-$platform" "$BIN_DIR/koreannet-gtin-gui"
      echo "설치됨: $BIN_DIR/koreannet-gtin-gui"
      ;;
  esac
fi

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "참고: $BIN_DIR 가 PATH에 없습니다. 셸 설정에 export PATH=\"$BIN_DIR:\$PATH\" 를 추가하세요." ;;
esac
"$BIN_DIR/koreannet-gtin" --version
