#!/bin/bash
# 安装 xiaohongshu-mcp 和 xiaohongshu-login 到 ~/.local/bin
# 用法: ./install-xiaohongshu-mcp.sh

set -e

ARCH=$(uname -m)
OS=$(uname -s)

case "$OS" in
  Darwin)
    if [ "$ARCH" = "arm64" ]; then
      SUFFIX="darwin-arm64"
    else
      SUFFIX="darwin-amd64"
    fi
    ;;
  Linux)
    if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
      SUFFIX="linux-arm64"
    else
      SUFFIX="linux-amd64"
    fi
    ;;
  *)
    echo "不支持的系统: $OS"
    exit 1
    ;;
esac

VERSION="v2026.02.27.1731-97a7b1e"
URL="https://github.com/xpzouying/xiaohongshu-mcp/releases/download/${VERSION}/xiaohongshu-mcp-${SUFFIX}.tar.gz"
BINDIR="$HOME/.local/bin"
TMPDIR=$(mktemp -d)

echo "检测到: $OS $ARCH -> $SUFFIX"
echo "下载: $URL"
echo ""

mkdir -p "$BINDIR"
if ! curl -sL --connect-timeout 30 --max-time 300 -o "$TMPDIR/xhs.tar.gz" "$URL"; then
  echo "下载失败（可能网络较慢）。请手动："
  echo "  1. 打开 https://github.com/xpzouying/xiaohongshu-mcp/releases"
  echo "  2. 下载 xiaohongshu-mcp-${SUFFIX}.tar.gz"
  echo "  3. 解压后执行："
  echo "     mkdir -p $BINDIR"
  echo "     mv xiaohongshu-mcp-${SUFFIX} $BINDIR/xiaohongshu-mcp"
  echo "     mv xiaohongshu-login-${SUFFIX} $BINDIR/xiaohongshu-login"
  echo "     chmod +x $BINDIR/xiaohongshu-mcp $BINDIR/xiaohongshu-login"
  rm -rf "$TMPDIR"
  exit 1
fi

cd "$TMPDIR"
tar -xzf xhs.tar.gz
# 解压后可能是 xiaohongshu-mcp-xxx 和 xiaohongshu-login-xxx
for f in xiaohongshu-mcp-*; do
  [ -f "$f" ] && mv "$f" "$BINDIR/xiaohongshu-mcp" && chmod +x "$BINDIR/xiaohongshu-mcp" && break
done
for f in xiaohongshu-login-*; do
  [ -f "$f" ] && mv "$f" "$BINDIR/xiaohongshu-login" && chmod +x "$BINDIR/xiaohongshu-login" && break
done
rm -rf "$TMPDIR"

if [ -x "$BINDIR/xiaohongshu-mcp" ] && [ -x "$BINDIR/xiaohongshu-login" ]; then
  echo "✅ 已安装到 $BINDIR"
  echo "   $BINDIR/xiaohongshu-mcp"
  echo "   $BINDIR/xiaohongshu-login"
  echo ""
  echo "请确保 PATH 包含: $BINDIR"
  echo "  export PATH=\"$BINDIR:\$PATH\""
else
  echo "⚠️ 解压后未找到预期可执行文件，请手动从 release 解压并放到 $BINDIR"
  exit 1
fi
