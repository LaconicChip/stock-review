#!/bin/bash
# start_web.sh — 启动本地网页服务，让 web/index.html 能读取 data/ 下的 JSON。
# 用法：bash scripts/start_web.sh [端口]，默认 8787
# 启动后浏览器打开 http://localhost:8787/web/index.html
set -e
PORT="${1:-8787}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "股票复盘网页服务："
echo "  根目录: $ROOT"
echo "  访问地址: http://localhost:${PORT}/web/index.html"
echo "按 Ctrl+C 停止。"
cd "$ROOT"
python3 -m http.server "$PORT"
