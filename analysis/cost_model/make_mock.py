#!/usr/bin/env python3
"""Fabricate mock GPU-seconds data for offline testing (no cloud or measured timing needed).

Outputs a JSON file that mimics the throughput-scaling analysis's single_job_stats.json format, so the model
can be tested without live data collection.

Usage:
    python3 make_mock.py
    python3 make_mock.py --out path/to/mock.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=HERE / "data" / "mock_single_job_stats.json",
                    help="output path for mock data")
    args = ap.parse_args(argv)

    # Plausible GPU-seconds per job for each service (synthetic, ~±20 % from config defaults)
    mock = {
        "rfdiffusion2-server": 380.0,
        "proteinmpnn-server":   85.0,
        "boltz-server":        620.0,
        "dockq-server":         28.0,
        "diffdock-server":     510.0,
        "reinvent-server":     1250.0,
        "flowmol-server":      320.0,
        "esmfold2-server":     190.0,
        "alphafold-server":    880.0,
        "genie3-server":        55.0,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(mock, f, indent=2)
    print(f"mock data: {len(mock)} services -> {args.out}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] if len(sys.argv) > 1 else None)