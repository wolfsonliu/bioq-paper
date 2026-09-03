#!/usr/bin/env bash
# Contract-conformance audit: collect → check → score → plot.
#
# Usage:
#   ./run_all.sh               # live: collect via bioq CLI, then full pipeline
#   ./run_all.sh --offline     # skip collection; re-check committed manifests
#
# Live mode needs an authenticated bioq CLI on PATH (or set BIOQ=/path/to/bioq).
# Plotting prefers uv (pulls matplotlib on demand) and falls back to system
# python3 when uv is unavailable.
set -euo pipefail
cd "$(dirname "$0")"

BIOQ="${BIOQ:-bioq}"
MODE="${1:---live}"

if [ "$MODE" != "--offline" ]; then
  echo "[1/3] collecting manifests via \`bioq describe\` + evaluating checklist ..."
  python3 audit.py --collect --bioq "$BIOQ"
else
  echo "[1/3] offline: re-checking committed manifests ..."
  python3 audit.py
fi

echo "[2/3] scoring + straggler tables ..."
python3 score.py

echo "[3/3] plotting conformance figure ..."
if uv run --with matplotlib python3 -c "import matplotlib" >/dev/null 2>&1; then
  uv run --with matplotlib python3 plot.py
else
  python3 plot.py
fi

echo "done. outputs in data/ and figures/"
