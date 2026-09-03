#!/usr/bin/env bash
# Offline orchestrator: mock → model → plot
# Usage: ./run_all.sh
# Requires uv (pulls python packages on demand).
set -euo pipefail
cd "$(dirname "$0")"

echo "[1/3] generating mock data ..."
python3 make_mock.py

echo "[2/3] running cost model ..."
python3 model.py

echo "[3/3] plotting figures ..."
uv run --with matplotlib,numpy python3 plot.py

echo "done. outputs in data/ and figures/"