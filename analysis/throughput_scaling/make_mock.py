#!/usr/bin/env python3
"""Fabricate mock timing data so analyze.py can be exercised
WITHOUT the ECS stack. NOT real data — self-test / example figure only.

Writes mock results/ and then runs analyze.py to produce example data/ files.
"""
from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path

from config import SERVICES, BATCH_SIZES, REPLICATES

HERE = Path(__file__).resolve().parent
R = HERE / "results"
BIOQ = R / "bioq"

# Mock parameters (realistic-ish)
SINGLE_TIMES = {
    "proteinmpnn": 150,      # GPU, hot: protein sequence design
    "mmseqs2": 60,            # GPU, hot: MSA search
    "rfdiffusion2": 500,      # GPU, warm: de novo protein generation
    "rfdiffusion": 120,       # GPU, warm: unconditional backbone
    "boltz": 300,             # GPU, warm: structure prediction
    "boltzgen": 300,          # GPU, warm: protein design
    "alphafold": 600,         # GPU, warm: structure prediction (heaviest)
    "reinvent": 60,           # GPU, warm: molecule generation
    "plip": 10,               # CPU, cold: interaction profiling
    "dockq": 5,               # CPU, cold: docking quality score
}
# Concurrency ceiling (simulate FC limit)
CONCURRENCY_CEIL = {
    "proteinmpnn": 8,
    "mmseqs2": 12,
    "rfdiffusion2": 4,
    "rfdiffusion": 6,
    "boltz": 4,
    "boltzgen": 4,
    "alphafold": 2,
    "reinvent": 6,
    "plip": 20,
    "dockq": 30,
}
# Cold start overhead per job (seconds)
COLD_START = 30.0


def _write_timing_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _write_meta_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def _make_bioq_batch(svc_cfg: dict, N: int, rep: int) -> None:
    svc = svc_cfg["name"]
    out_dir = BIOQ / svc / f"N_{N}" / f"rep_{rep}"
    single_t = SINGLE_TIMES[svc]
    conc_ceil = CONCURRENCY_CEIL[svc]
    seed_start = svc_cfg["seed_start"] if svc_cfg["seed_start"] is not None else 0

    # Simulate serverless dispatch: jobs run in waves of conc_ceil
    wall_start = 1500.0  # arbitrary base timestamp
    timing_rows = []
    fake_job_ids = []
    makespan = 0.0

    for i in range(N):
        job_id = f"mock_{svc}_{N}_{rep}_{i:04d}"
        fake_job_ids.append(job_id)

        # Which wave?
        wave = i // conc_ceil
        wave_offset = i % conc_ceil

        # Within a wave, jobs start at slightly staggered times (cold start +
        # small variance)
        wave_start = wall_start + wave * single_t * 1.05  # 5% overhead
        t_submit = wall_start + i * 0.1  # submit at ~0.1s intervals
        cold = COLD_START * (1.0 + 0.5 * random.random()) if wave == 0 else 5.0 * random.random()
        t_running = wave_start + cold + wave_offset * 2.0
        t_completed = t_running + single_t * (0.8 + 0.4 * random.random())

        timing_rows.append({
            "job_id": job_id,
            "t_submit": round(t_submit, 3),
            "t_running": round(t_running, 3),
            "t_completed": round(t_completed, 3),
            "status": "completed",
            "seed": seed_start + i,
        })
        makespan = max(makespan, t_completed - wall_start)

    _write_timing_csv(
        out_dir / "timing.csv", timing_rows,
        ["job_id", "t_submit", "t_running", "t_completed", "status", "seed"])

    # Concurrency history
    n_completed = sum(1 for r in timing_rows if r["status"] == "completed")
    _write_meta_json(out_dir / "meta.json", {
        "svc": svc, "endpoint": svc_cfg["endpoint"], "N": N, "rep": rep,
        "makespan_s": round(makespan, 2),
        "peak_concurrency": min(conc_ceil, N),
        "n_completed": n_completed,
        "n_failed": 0, "n_cancelled": 0, "n_pending": 0,
        "bioq_version": "mock",
        "gateway_url": "", "timestamp": "mock",
    })

    # Concurrency history
    hist = []
    for t in range(0, int(makespan) + 10, 10):
        n_running = 0
        for r in timing_rows:
            if r["t_running"] and r["t_completed"]:
                if r["t_running"] <= t + wall_start <= r["t_completed"]:
                    n_running += 1
        n_pending = N - n_running - sum(1 for r in timing_rows
                                        if r["t_completed"] and r["t_completed"] <= t + wall_start)
        hist.append({"timestamp": t + wall_start, "n_running": n_running, "n_pending": max(0, n_pending)})
    _write_timing_csv(out_dir / "concurrency.csv", hist,
                      ["timestamp", "n_running", "n_pending"])


def main() -> None:
    random.seed(42)

    for svc_cfg in SERVICES:
        svc = svc_cfg["name"]
        print(f"Generating mock data for {svc} ...")

        for N in BATCH_SIZES:
            for rep in range(1, REPLICATES + 1):
                _make_bioq_batch(svc_cfg, N, rep)

    print(f"Mock data written under {R.relative_to(HERE)}/")
    print("Now run: python3 analyze.py")


if __name__ == "__main__":
    main()