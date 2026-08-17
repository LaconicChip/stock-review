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
#
# Windows/Git Bash 兼容说明：
# - `nohup ... &` 的 $! 是 MSYS 伪 PID，并非 Windows 原生 PID，
#   直接 kill 杀不到真实进程（会留下孤儿）。因此本脚本一律
#   通过 netstat 按端口反查真实 PID，并用 taskkill 终止。

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${2:-8787}"
PIDFILE="$ROOT/.stock-review.pid"
LOGFILE="$ROOT/.stock-review.log"
URL="http://localhost:${PORT}/web/index.html"

# 反查监听 $PORT 的真实进程 PID（Windows netstat 输出，最后一列为 PID）。
# 列布局: Proto(1) Local(2) Foreign(3) State(4) PID(5)
# 无监听时输出为空。
get_listen_pid() {
  netstat -ano 2>/dev/null |
    awk -v port="$PORT" '$2 ~ ":" port "$" && $4 == "LISTENING" {print $NF; exit}'
}

# 是否运行中：以端口是否有监听为准（不依赖 pid 文件，避免残留误判）
is_running() {
  [[ -n "$(get_listen_pid)" ]]
}

# 解析可用的 Python 解释器。
# Windows 上 PATH 里的 python3/python 可能是 Microsoft Store 的"应用执行别名"
# （AppInstallerPythonRedirector.exe），调用后静默退出（exit 49、无输出），
# 因此必须校验 `--version` 的真实输出，而不能只看退出码。
resolve_python() {
  local c v
  for c in python3 python; do
    v="$($c --version 2>&1)"
    case "$v" in
      Python*) echo "$c"; return 0 ;;
    esac
  done
  # Git Bash 下常见真实安装路径兜底（无空格路径）
  local p
  for p in "$LOCALAPPDATA"/Programs/Python/Python*/python.exe /c/Python*/python.exe; do
    [ -f "$p" ] && { echo "$p"; return 0; }
  done
  return 1
}

# 强制终止进程。taskkill 需 MSYS_NO_PATHCONV=1 防止参数被路径转换。
kill_pid() {
  local pid="$1"
  [[ -n "$pid" ]] || return 1
  MSYS_NO_PATHCONV=1 taskkill /F /PID "$pid" >/dev/null 2>&1
}

# 等待端口释放（最多约 5 秒）
wait_port_free() {
  local _
  for _ in $(seq 1 10); do
    [[ -n "$(get_listen_pid)" ]] || return 0
    sleep 0.5
  done
  return 1
}

do_start() {
  if is_running; then
    echo "⚠️  服务已在运行（PID $(get_listen_pid)）：$URL"
    exit 0
  fi
  cd "$ROOT"
  echo "启动股票复盘网页服务："
  echo "  根目录: $ROOT"
  echo "  端口:   $PORT"
  local py
  py="$(resolve_python)" || { echo "❌ 未找到可用的 Python，请安装 Python 并确保能运行 'python --version'。"; exit 1; }
  nohup $py -m http.server "$PORT" > "$LOGFILE" 2>&1 &
  # Windows 下 python 冷启动可能较慢，轮询等待端口监听（最多约 5 秒）
  local pid=""
  local _
  for _ in $(seq 1 10); do
    pid="$(get_listen_pid)"
    [[ -n "$pid" ]] && break
    sleep 0.5
  done
  if [[ -n "$pid" ]]; then
    echo "$pid" > "$PIDFILE"
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
    return 0   # 用 return 而非 exit，避免中断 restart 流程
  fi
  local pid
  pid="$(cat "$PIDFILE" 2>/dev/null)"
  # 优先用 pid 文件记录的 PID；若失效则按端口反查
  if ! kill_pid "$pid"; then
    pid="$(get_listen_pid)"
    kill_pid "$pid"
  fi
  echo "正在停止服务（PID $pid）..."
  if wait_port_free; then
    echo "✅ 已停止"
  else
    echo "⚠️  端口 $PORT 仍有监听（PID $(get_listen_pid)），停止可能失败"
    exit 1
  fi
  rm -f "$PIDFILE"
}

do_status() {
  local pid
  pid="$(get_listen_pid)"
  if [[ -n "$pid" ]]; then
    echo "✅ 服务运行中（PID $pid）"
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
