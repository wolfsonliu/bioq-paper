#!/usr/bin/env python3
"""Throughput-scaling collector — BIOQ (async) path.  ***RUN ON ECS (or any host that can
reach the gateway).***

For each service × batch-size N × replicate, submits N independent jobs via
``bioq submit`` (async), polls all to completion, and records per-job timing
(submit/running/completed) plus peak concurrency.

Usage:
    python3 collect_bioq.py [--svc proteinmpnn] [--N 10] [--rep 1] [--cooldown 600]
    python3 collect_bioq.py --help

All flags also accept TPUT_* env vars as fallback:

    TPUT_SVC=proteinmpnn TPUT_N=10 TPUT_REP=1 python3 collect_bioq.py

Deps: python3 + bioq CLI. No pip installs.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from config import BATCH_SIZES, REPLICATES, POLL_INTERVAL, POLL_TIMEOUT, WARM_UP, SERVICES, COOLDOWN

HERE = Path(__file__).resolve().parent
INPUTS = HERE / "inputs"
OUTROOT = HERE / "results" / "bioq"

TERMINAL = {"completed", "failed", "cancelled"}


def _bioq_version() -> str:
    try:
        return subprocess.run(["bioq", "--version"], capture_output=True,
                              text=True, check=False).stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def _global_flags() -> list[str]:
    flags = []
    if os.environ.get("BIOQ_GATEWAY_URL"):
        flags += ["--gateway-url", os.environ["BIOQ_GATEWAY_URL"]]
    if os.environ.get("BIOQ_PROFILE"):
        flags += ["--profile", os.environ["BIOQ_PROFILE"]]
    return flags


def _submit_job(svc: str, endpoint: str, files: dict,
                params: dict, set_json: dict | None = None) -> tuple[str, float]:
    """Submit one job via 'bioq submit', return (job_id, submit_time)."""
    argv = ["bioq", *_global_flags(), "submit", svc, endpoint]
    for field, fname in files.items():
        argv += ["--file", f"{field}={INPUTS / fname}"]
    for k, v in params.items():
        argv += ["--set", f"{k}={v}"]
    if set_json:
        for k, v in set_json.items():
            argv += ["--set-json", f"{k}={v}"]
    argv += ["--output", "json"]

    t_submit = time.time()
    proc = subprocess.run(argv, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"bioq submit failed (rc={proc.returncode}): "
                           f"{proc.stderr[:500]}")
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"bioq submit JSON parse error: {proc.stdout[:500]}")
    job_id = result.get("job_id", "")
    if not job_id:
        raise RuntimeError(f"bioq submit returned no job_id: {result}")
    return job_id, t_submit


def _status(svc: str, endpoint: str, job_id: str) -> tuple[dict, float]:
    """Check job status via 'bioq status', return (status_dict, time)."""
    argv = ["bioq", *_global_flags(), "status", job_id, "--output", "json"]
    t = time.time()
    proc = subprocess.run(argv, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return {"status": "unknown", "detail": f"status rc={proc.returncode}"}, t
    try:
        return json.loads(proc.stdout), t
    except json.JSONDecodeError:
        return {"status": "unknown", "detail": f"parse error: {proc.stdout[:200]}"}, t


def run_batch(svc_cfg: dict, N: int, rep: int) -> Path:
    """Submit N jobs, poll to completion, record per-job timing."""
    svc = svc_cfg["name"]
    endpoint = svc_cfg["endpoint"]
    out_dir = OUTROOT / svc / f"N_{N}" / f"rep_{rep}"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    base_params = dict(svc_cfg["params"])
    files = dict(svc_cfg["files"])
    seed_start = svc_cfg["seed_start"]
    set_json = svc_cfg.get("set_json")  # optional --set-json params

    # ---- Phase 1: submit all N jobs ----
    print(f"\n[submit] {svc} N={N} rep={rep}: submitting {N} jobs ...")
    jobs = []  # list of {job_id, t_submit, params, t_running, t_completed, status}
    for i in range(N):
        params = dict(base_params)
        if seed_start is not None:
            params["seed"] = seed_start + i
        job_id, t_sub = _submit_job(svc, endpoint, files, params, set_json)
        jobs.append({
            "job_id": job_id,
            "t_submit": t_sub,
            "params": params,
            "t_running": None,
            "t_completed": None,
            "status": "pending",
        })
        print(f"  job {i+1}/{N}: {job_id} submitted")

    # ---- Phase 2: poll all to completion ----
    print(f"[poll]   {svc} N={N} rep={rep}: polling {N} jobs ...")
    deadline = time.time() + POLL_TIMEOUT
    pending = set(range(N))
    peak_concurrency = 0
    concurrency_history = []  # list of (timestamp, count_running)

    while pending and time.time() < deadline:
        now = time.time()
        n_running = 0
        for idx in list(pending):
            j = jobs[idx]
            try:
                status_dict, t = _status(svc, endpoint, j["job_id"])
            except Exception as e:
                print(f"  !! status error for {j['job_id']}: {e}")
                continue

            new_status = status_dict.get("status", "unknown")
            if new_status != j["status"]:
                if new_status == "running" and j["t_running"] is None:
                    j["t_running"] = t
                    print(f"  job {j['job_id']}: pending -> running  "
                          f"(Δ={t - j['t_submit']:.1f}s from submit)")
                if new_status in TERMINAL:
                    j["t_completed"] = t
                    j["status"] = new_status
                    pending.remove(idx)
                    makespan = t - j["t_submit"]
                    print(f"  job {j['job_id']}: {new_status}  "
                          f"(makespan={makespan:.1f}s, "
                          f"running→done={t - (j['t_running'] or t):.1f}s)")
                    continue
            j["status"] = new_status
            if new_status == "running":
                n_running += 1

        if n_running > peak_concurrency:
            peak_concurrency = n_running
        concurrency_history.append((now, n_running, len(pending)))

        if pending:
            time.sleep(POLL_INTERVAL)

    if pending:
        print(f"  !! TIMEOUT: {len(pending)} jobs still pending after {POLL_TIMEOUT}s")
        for idx in pending:
            print(f"    {jobs[idx]['job_id']}: last status={jobs[idx]['status']}")

    dt = time.time() - min(j["t_submit"] for j in jobs)
    print(f"[done]   {svc} N={N} rep={rep}: makespan={dt:.1f}s, "
          f"peak_concurrency={peak_concurrency}")

    # ---- Write results ----
    timing_rows = []
    for j in jobs:
        timing_rows.append({
            "job_id": j["job_id"],
            "t_submit": round(j["t_submit"], 3),
            "t_running": round(j["t_running"], 3) if j["t_running"] else "",
            "t_completed": round(j["t_completed"], 3) if j["t_completed"] else "",
            "status": j["status"],
            "seed": j["params"].get("seed", ""),
        })

    with (out_dir / "timing.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["job_id", "t_submit", "t_running",
                                           "t_completed", "status", "seed"])
        w.writeheader()
        w.writerows(timing_rows)

    meta = {
        "svc": svc, "endpoint": endpoint, "N": N, "rep": rep,
        "makespan_s": round(dt, 2),
        "peak_concurrency": peak_concurrency,
        "n_completed": sum(1 for j in jobs if j["status"] == "completed"),
        "n_failed": sum(1 for j in jobs if j["status"] == "failed"),
        "n_cancelled": sum(1 for j in jobs if j["status"] == "cancelled"),
        "n_pending": len(pending),
        "bioq_version": _bioq_version(),
        "gateway_url": os.environ.get("BIOQ_GATEWAY_URL", ""),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))

    # Also write concurrency history for analysis
    with (out_dir / "concurrency.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["timestamp", "n_running", "n_pending"])
        w.writerows(concurrency_history)

    return out_dir


def main() -> None:
    def _env_int(key: str) -> int | None:
        v = os.environ.get(key)
        return int(v) if v else None

    def _env_float(key: str) -> float | None:
        v = os.environ.get(key)
        return float(v) if v else None

    ap = argparse.ArgumentParser(
        description="Throughput scaling — bioq (async) collector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Precedence: CLI flags > TPUT_* env vars > config.py defaults.\n"
               "Services: " + ", ".join(s["name"] for s in SERVICES),
    )
    ap.add_argument("--svc", "-s", default=os.environ.get("TPUT_SVC"),
                    help="limit to one service (default: all)")
    ap.add_argument("--N", "-n", type=int, default=_env_int("TPUT_N"),
                    help="limit to one batch size (default: all in config)")
    ap.add_argument("--rep", "-r", type=int, default=_env_int("TPUT_REP"),
                    help="replicates per (service, N) (default: config REPLICATES)")
    ap.add_argument("--cooldown", "-c", type=float, default=_env_float("TPUT_COOLDOWN"),
                    help="seconds between replicates (default: config COOLDOWN)")
    args = ap.parse_args()

    if not shutil.which("bioq"):
        raise SystemExit("bioq not found — install the client on the ECS host")

    batch_sizes = [args.N] if args.N is not None else BATCH_SIZES
    replicates = args.rep if args.rep is not None else REPLICATES
    cooldown = args.cooldown if args.cooldown is not None else COOLDOWN

    services = [s for s in SERVICES if args.svc is None or s["name"] == args.svc]

    if not services:
        raise SystemExit(f"no service matched --svc={args.svc!r}")

    for svc_cfg in services:
        svc = svc_cfg["name"]
        print(f"\n{'='*60}")
        print(f"=== {svc} ({svc_cfg['tier']} tier)")
        print(f"{'='*60}")

        # Warm-up: submit a small batch to warm the FC tier
        if WARM_UP:
            print(f"\n--- warm-up: {svc} N=1 ---")
            warm_dir = OUTROOT / svc / "warmup"
            if warm_dir.exists():
                shutil.rmtree(warm_dir)
            try:
                params = dict(svc_cfg["params"])
                if svc_cfg["seed_start"] is not None:
                    params["seed"] = 999999
                files = dict(svc_cfg["files"])
                set_json = svc_cfg.get("set_json")
                job_id, _ = _submit_job(svc, svc_cfg["endpoint"], files, params, set_json)
                # Poll just this one job to completion
                deadline = time.time() + POLL_TIMEOUT
                while time.time() < deadline:
                    status_dict, _ = _status(svc, svc_cfg["endpoint"], job_id)
                    if status_dict.get("status") in TERMINAL:
                        break
                    time.sleep(POLL_INTERVAL)
                print(f"  warm-up {job_id}: {status_dict.get('status')}")
            except Exception as e:
                print(f"  warm-up skipped ({e})")
            warm_dir.mkdir(parents=True, exist_ok=True)
            (warm_dir / "meta.json").write_text(
                json.dumps({"warmup": True, "svc": svc, "job_id": job_id}, indent=2))

        for N in batch_sizes:
            for rep in range(1, replicates + 1):
                run_batch(svc_cfg, N, rep)
                if rep < replicates and cooldown > 0:
                    print(f"\n[cooldown] waiting {cooldown:.0f}s before next replicate ...")
                    time.sleep(cooldown)

    print(f"\n{'='*60}")
    print("All bioq collection runs complete.")
    print(f"Results in {OUTROOT.relative_to(HERE)}/")


if __name__ == "__main__":
    main()
