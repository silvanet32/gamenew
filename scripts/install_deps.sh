#!/usr/bin/env bash
set -euo pipefail

# Backend (Flask)
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Frontend (React + Vite)
cd frontend
npm install

echo "Dependências backend/frontend instaladas com sucesso."
