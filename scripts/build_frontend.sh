#!/usr/bin/env bash
set -euo pipefail

cd frontend
npm run build

echo "Build concluído em frontend/dist"
