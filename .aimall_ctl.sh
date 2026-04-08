#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$ROOT_DIR/.run"
LOG_DIR="$ROOT_DIR/logs"
BACKEND_DIR="$ROOT_DIR/backend"
ADMIN_DIR="$ROOT_DIR/frontend-admin"
MALL_DIR="$ROOT_DIR/frontend-mall"

BACKEND_PORT=18080
ADMIN_PORT=3100
MALL_PORT=3101

BACKEND_PID_FILE="$RUN_DIR/backend.pid"
ADMIN_PID_FILE="$RUN_DIR/frontend-admin.pid"
MALL_PID_FILE="$RUN_DIR/frontend-mall.pid"

mkdir -p "$RUN_DIR" "$LOG_DIR"

log() {
  printf '[AiMall] %s\n' "$*"
}

port_pids() {
  local port="$1"
  lsof -nP -iTCP:"$port" -sTCP:LISTEN 2>/dev/null | awk 'NR>1 {print $2}' | sort -u
}

kill_pid_file() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file" 2>/dev/null || true)"
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      sleep 1
      kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
  fi
}

kill_port() {
  local port="$1"
  local pids
  pids="$(port_pids "$port" || true)"
  if [[ -n "${pids:-}" ]]; then
    while IFS= read -r pid; do
      [[ -z "$pid" ]] && continue
      kill "$pid" 2>/dev/null || true
      sleep 1
      kill -9 "$pid" 2>/dev/null || true
    done <<< "$pids"
  fi
}

wait_port() {
  local port="$1"
  local retries="${2:-30}"
  local i=0
  while (( i < retries )); do
    if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  return 1
}

backend_start() {
  if lsof -nP -iTCP:"$BACKEND_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    log "后端已在运行 (port $BACKEND_PORT)"
    return 0
  fi
  if [[ ! -x "$BACKEND_DIR/.venv/bin/python" ]]; then
    log "未找到后端虚拟环境：$BACKEND_DIR/.venv"
    return 1
  fi
  log "启动后端 (Django:$BACKEND_PORT)..."
  nohup bash -lc "cd '$BACKEND_DIR' && '$BACKEND_DIR/.venv/bin/python' manage.py migrate --noinput && '$BACKEND_DIR/.venv/bin/python' manage.py runserver 127.0.0.1:$BACKEND_PORT --noreload" > "$LOG_DIR/backend.log" 2>&1 &
  echo $! > "$BACKEND_PID_FILE"
  if wait_port "$BACKEND_PORT" 40; then
    log "后端启动成功: http://127.0.0.1:$BACKEND_PORT"
  else
    log "后端启动失败，请查看日志: $LOG_DIR/backend.log"
    return 1
  fi
}

backend_stop() {
  log "停止后端..."
  kill_pid_file "$BACKEND_PID_FILE"
  kill_port "$BACKEND_PORT"
  log "后端已停止"
}

frontend_start() {
  if lsof -nP -iTCP:"$ADMIN_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    log "管理端已在运行 (port $ADMIN_PORT)"
  else
    if [[ ! -d "$ADMIN_DIR/dist" ]]; then
      log "管理端 dist 不存在，请先在 $ADMIN_DIR 执行 npm run build"
      return 1
    fi
    log "启动管理端 (preview:$ADMIN_PORT)..."
    nohup zsh -lc "cd '$ADMIN_DIR' && npx vite preview --host 127.0.0.1 --port $ADMIN_PORT --strictPort" > "$LOG_DIR/frontend-admin.log" 2>&1 &
    echo $! > "$ADMIN_PID_FILE"
    wait_port "$ADMIN_PORT" 40 || { log "管理端启动失败，请查看 $LOG_DIR/frontend-admin.log"; return 1; }
  fi

  if lsof -nP -iTCP:"$MALL_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    log "商城端已在运行 (port $MALL_PORT)"
  else
    if [[ ! -d "$MALL_DIR/dist" ]]; then
      log "商城端 dist 不存在，请先在 $MALL_DIR 执行 npm run build"
      return 1
    fi
    log "启动商城端 (preview:$MALL_PORT)..."
    nohup zsh -lc "cd '$MALL_DIR' && npx vite preview --host 127.0.0.1 --port $MALL_PORT --strictPort" > "$LOG_DIR/frontend-mall.log" 2>&1 &
    echo $! > "$MALL_PID_FILE"
    wait_port "$MALL_PORT" 40 || { log "商城端启动失败，请查看 $LOG_DIR/frontend-mall.log"; return 1; }
  fi

  log "前端启动完成: 管理端 http://127.0.0.1:$ADMIN_PORT | 商城端 http://127.0.0.1:$MALL_PORT"
}

frontend_stop() {
  log "停止前端（管理端+商城端）..."
  kill_pid_file "$ADMIN_PID_FILE"
  kill_pid_file "$MALL_PID_FILE"
  kill_port "$ADMIN_PORT"
  kill_port "$MALL_PORT"
  log "前端已停止"
}

backend_restart() {
  backend_stop || true
  backend_start
}

frontend_restart() {
  frontend_stop || true
  frontend_start
}

usage() {
  cat <<USAGE
Usage: $0 <backend_start|backend_stop|backend_restart|frontend_start|frontend_stop|frontend_restart>
USAGE
}

cmd="${1:-}"
case "$cmd" in
  backend_start) backend_start ;;
  backend_stop) backend_stop ;;
  backend_restart) backend_restart ;;
  frontend_start) frontend_start ;;
  frontend_stop) frontend_stop ;;
  frontend_restart) frontend_restart ;;
  *) usage; exit 1 ;;
esac
