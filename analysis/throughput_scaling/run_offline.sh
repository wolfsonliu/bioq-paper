#!/usr/bin/env bash
# Offline analysis: process collected FC timing data and render figures.
# Run AFTER collect_bioq.py has populated results/bioq/ (on ECS).
# Needs uv (for scipy + matplotlib).
set -euo pipefail
cd "$(dirname "$0")"
uv run --with scipy python analyze.py "$@"
uv run --with matplotlib --with numpy python plot_aliyun.py
uv run --with matplotlib --with numpy --with scipy python plot_aliyun_by_service.py
echo "done. see data/throughput.csv, data/scaling_summary.json, data/single_job_stats.json,"
echo "data/statistical_tests.{json,csv}, and figures/E3_bioq*.pdf"