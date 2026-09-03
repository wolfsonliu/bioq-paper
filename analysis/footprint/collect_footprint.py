#!/usr/bin/env python3
"""Footprint sub-analysis — best-effort image footprint vs the bioq thin client (collection).

Records the on-disk size of any service image already built locally (via
``docker image ls``) and measures the bioq client footprint (its runtime deps in
a throwaway venv). Service images that are not built on this host are left
unmeasured, so the *fleet* total here is an explicit lower bound / partial
measurement, not the full number. The headline dependency-incompatibility result
does not depend on this part.

Inputs : data/signatures.csv
Outputs: data/footprint.csv  (render the figure with ``plot.py``)

Plotting lives in the sibling ``plot.py`` (offline, reads the CSV), per
``docs/plotting-style-guide.md`` §6.
"""
from __future__ import annotations

import csv
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"


def _size_to_mb(s: str) -> float | None:
    m = re.match(r"([\d.]+)\s*([KMGT]?B)", s.strip(), re.IGNORECASE)
    if not m:
        return None
    val, unit = float(m.group(1)), m.group(2).upper()
    return val * {"B": 1e-6, "KB": 1e-3, "MB": 1, "GB": 1e3, "TB": 1e6}[unit]


def _docker_images() -> dict[str, float]:
    """repo(:tag stripped) -> size MB, keeping the largest tag seen per repo."""
    if not shutil.which("docker"):
        return {}
    try:
        out = subprocess.run(
            ["docker", "image", "ls", "--format", "{{.Repository}}\t{{.Size}}"],
            capture_output=True, text=True, timeout=30, check=True).stdout
    except (subprocess.SubprocessError, OSError):
        return {}
    sizes: dict[str, float] = {}
    for line in out.splitlines():
        if "\t" not in line:
            continue
        repo, size = line.split("\t", 1)
        mb = _size_to_mb(size)
        if mb is None:
            continue
        repo = repo.split("/")[-1]  # strip registry/namespace
        sizes[repo] = max(sizes.get(repo, 0.0), mb)
    return sizes


def _client_footprint_mb() -> float | None:
    """Install the bioq client's runtime deps into a temp venv and measure."""
    uv = shutil.which("uv")
    if not uv:
        return None
    with tempfile.TemporaryDirectory() as td:
        venv = Path(td) / "v"
        try:
            subprocess.run([uv, "venv", str(venv)], capture_output=True,
                           timeout=120, check=True)
            subprocess.run([uv, "pip", "install", "--python",
                            str(venv / "bin" / "python"), "httpx"],
                           capture_output=True, timeout=300, check=True)
        except (subprocess.SubprocessError, OSError):
            return None
        total = sum(p.stat().st_size for p in venv.rglob("*") if p.is_file())
        return total / 1e6


def main() -> None:
    services = [ln.split(",")[0] for ln in
                (DATA / "signatures.csv").read_text().splitlines()[1:]]
    imgs = _docker_images()

    rows = []
    for svc in services:
        mb = imgs.get(svc) or imgs.get(f"{svc}-fn")
        rows.append({"service": svc,
                     "image_size_mb": round(mb, 1) if mb else "",
                     "status": "measured" if mb else "not_built_locally"})

    client_mb = _client_footprint_mb()
    rows.append({"service": "bioq (thin client)",
                 "image_size_mb": round(client_mb, 1) if client_mb else "",
                 "status": "measured (runtime deps venv)" if client_mb else "unknown"})

    with (DATA / "footprint.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["service", "image_size_mb", "status"])
        w.writeheader()
        w.writerows(rows)

    n_measured = sum(1 for r in rows if r["status"].startswith("measured")
                     and r["service"] != "bioq (thin client)")
    print(f"measured {n_measured}/{len(services)} service images locally "
          f"(rest not built on this host)")
    print(f"bioq client footprint: "
          f"{client_mb:.1f} MB" if client_mb else "client footprint: n/a")
    print(f"wrote {(DATA / 'footprint.csv').relative_to(HERE)}")
    print("plot with: uv run --with matplotlib python plot.py")


if __name__ == "__main__":
    main()