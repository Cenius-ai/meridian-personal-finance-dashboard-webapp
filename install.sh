#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "==> Upgrading packaging tooling"
pip3 install --upgrade pip setuptools wheel >/dev/null

echo "==> Installing Python dependencies"
pip3 install -r requirements.txt

echo "==> Regenerating deterministic demo data (idempotent)"
python3 seed.py

echo "==> Verifying imports"
python3 -c "import app; import api; from data import repository; print('imports OK')"

echo
echo "Setup complete. Start the app with:"
echo "  python3 app.py"
