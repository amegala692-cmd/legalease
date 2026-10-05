#!/usr/bin/env bash
set -e
source .venv/bin/activate
(uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 > backend.log 2>&1 & echo $! > .backend.pid)
trap 'kill $(cat .backend.pid) 2>/dev/null || true' EXIT
streamlit run frontend/app.py
