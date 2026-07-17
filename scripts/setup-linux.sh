#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
[ -f .env ] || cp .env.example .env
cd "$ROOT/frontend"
npm install
[ -f .env ] || cp .env.example .env
echo "Setup complete. Use scripts/start-backend.sh and scripts/start-frontend.sh"
