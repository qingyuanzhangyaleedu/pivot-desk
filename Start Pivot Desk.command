#!/bin/zsh
set -eu
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python || ! -d frontend/node_modules ]]; then
  echo "Run the install steps in README.md first."
  read -r "?Press Enter to close. "
  exit 1
fi
npm --prefix frontend run build
( sleep 2; open http://localhost:8000 ) &
cd backend
exec ../.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
