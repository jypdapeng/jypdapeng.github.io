#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/backend"
if python3 -m venv .venv 2>/dev/null; then
  source .venv/bin/activate
fi
pip install -r requirements.txt -q
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
