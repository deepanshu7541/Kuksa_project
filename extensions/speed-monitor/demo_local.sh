#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# --- Detect a working Python ---
PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  # try common brew paths
  if [ -x /opt/homebrew/bin/python3 ]; then PY=/opt/homebrew/bin/python3
  elif [ -x /usr/local/bin/python3 ]; then PY=/usr/local/bin/python3
  else
    echo "❌ Could not find python3. Please 'brew install python' first." >&2
    exit 1
  fi
fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-55556}"   # your compose maps 55556(host) -> 55555(container)

# --- Fresh venv to avoid mixing with old 2.7 pip ---
if [ -d .venv ]; then
  echo "↻ Recreating virtualenv to ensure clean Python..."
  rm -rf .venv
fi

"$PY" -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate

# Always use 'python -m pip' to avoid wrong pip on PATH
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "[1/2] High threshold (no alerts expected, 6s)"
python -m speedMonitor.main --host "$HOST" --port "$PORT" --max-speed 200 --csv alerts_high.csv & PID=$!
sleep 6 && kill -TERM $PID || true
sleep 1

echo "[2/2] Low threshold (alerts expected, 6s)"
python -m speedMonitor.main --host "$HOST" --port "$PORT" --max-speed 20 --csv alerts_low.csv & PID=$!
sleep 6 && kill -TERM $PID || true
sleep 1

echo "Sample alerts:"
head -n 5 alerts_low.csv || true
