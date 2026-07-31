#!/bin/bash
# start_web.sh — 本地网页服务快速启停控制器
# 让 web/index.html 能读取 data/ 下的 JSON。
# 用法：
#   bash scripts/start_web.sh            # 启动（默认端口 8787，后台守护）
#   bash scripts/start_web.sh start [端口]
#   bash scripts/start_web.sh stop
#   bash scripts/start_web.sh restart [端口]
#   bash scripts/start_web.sh status
# 默认端口 8787，与既有约定一致；后台运行，停止用 stop。

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${2:-8787}"
PIDFILE="$ROOT/.stock-review.pid"
LOGFILE="$ROOT/.stock-review.log"
URL="http://localhost:${PORT}/web/index.html"

is_running() {
  [[ -f "$PIDFILE" ]] || return 1
  local pid
  pid="$(cat "$PIDFILE" 2>/dev/null)"
  [[ -n "$pid" ]] || return 1
  kill -0 "$pid" 2>/dev/null
}

# 端口是否已被监听（可能是上次未正常退出的服务）。
# 优先用 lsof 探测真实监听进程；仅当 lsof 不可用时才用 curl 兜底。
port_occupied() {
  if command -v lsof >/dev/null 2>&1; then
    if lsof -iTCP:"$PORT" -sTCP:LISTEN -t 2>/dev/null | grep -q .; then
      return 0
    fi
    return 1   # lsof 可用且未见监听 → 直接判空闲，不用 curl（避开代理误判）
  fi
  # 仅当 lsof 不可用时，才用 curl 兜底（能拿到任意响应即视为占用）
  if curl -s -o /dev/null --max-time 2 "http://localhost:${PORT}/" 2>/dev/null; then
    return 0
  fi
  return 1
}

do_start() {
  if is_running; then
    echo "⚠️  服务已在运行（PID $(cat "$PIDFILE")）：$URL"
    exit 0
  fi
  # 端口已被占用（可能是上次未正常退出的服务）则提示，不重复拉起
  if port_occupied; then
    echo "⚠️  端口 $PORT 已被占用（可能已有服务在运行）。如需重启请先执行 stop，或换端口。"
    exit 1
  fi
  cd "$ROOT"
  echo "启动股票复盘网页服务："
  echo "  根目录: $ROOT"
  echo "  端口:   $PORT"
  nohup python3 -m http.server "$PORT" > "$LOGFILE" 2>&1 &
  local pid=$!
  echo "$pid" > "$PIDFILE"
  sleep 1
  if is_running; then
    echo "✅ 已启动（PID $pid）"
    echo "   访问地址: $URL"
    echo "   停止命令: bash scripts/start_web.sh stop"
  else
    echo "❌ 启动失败，查看日志：$LOGFILE"
    rm -f "$PIDFILE"
    exit 1
  fi
}

do_stop() {
  if ! is_running; then
    echo "⚠️  服务未运行"
    rm -f "$PIDFILE"
    exit 0
  fi
  local pid
  pid="$(cat "$PIDFILE")"
  echo "正在停止服务（PID $pid）..."
  kill "$pid" 2>/dev/null || true
  local _
  for _ in $(seq 1 10); do
    kill -0 "$pid" 2>/dev/null || break
    sleep 0.5
  done
  if kill -0 "$pid" 2>/dev/null; then
    echo "  未优雅退出，强制终止（kill -9）..."
    kill -9 "$pid" 2>/dev/null || true
  fi
  rm -f "$PIDFILE"
  echo "✅ 已停止"
}

do_status() {
  if is_running; then
    echo "✅ 服务运行中（PID $(cat "$PIDFILE")）"
    echo "   访问地址: $URL"
  else
    echo "⭕ 服务未运行"
    rm -f "$PIDFILE"
  fi
}

case "${1:-start}" in
  start)   do_start ;;
  stop)    do_stop ;;
  restart) do_stop; do_start ;;
  status)  do_status ;;
  *) echo "未知命令：$1"; echo "用法：bash scripts/start_web.sh [start|stop|restart|status] [端口]"; exit 1 ;;
esac
