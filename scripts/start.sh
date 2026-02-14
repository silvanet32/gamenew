#!/usr/bin/env bash
set -euo pipefail

if [ ! -d ".venv" ]; then
  echo "Ambiente virtual não encontrado (.venv). Rode: ./scripts/install_deps.sh"
  exit 1
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python app.py
