#!/bin/sh
set -e

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  uv venv .venv --quiet
fi

uv pip install --python .venv/bin/python --quiet -r requirements.txt

if [ "$1" = "test" ]; then
  exec .venv/bin/python -m pytest tests/ -v
fi

exec .venv/bin/python -m uvicorn main:app --reload --host 0.0.0.0 --port "${PORT:-3000}"
