#!/usr/bin/env python3
"""Compute-barrier figure: fleet VRAM vs hardware thresholds.

Draws per-service sorted horizontal bars for the FC-provisioned GPU
(`fc_vram_gb`), with the best-known minimum overlaid (`min_vram_gb`):
solid diamonds = documented floors (`kind == minimum`), hollow circles =
inferred estimates (`kind == inferred`, low confidence). Red dashed lines mark
the laptop/consumer/workstation thresholds (4 / 8 / 24 GB). Styled to match the
throughput-scaling figures (white canvas, `#E8F6F3` axis background, left-aligned
bold titles, brand palette).

Usage:
  uv run --with matplotlib python plot.py              # data/vram.csv -> figures/
  uv run --with matplotlib python plot.py --demo       # synthetic data (no CSV needed)
"""

from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent
DEFAULT_CSV = HERE / "data" / "vram.csv"
DEFAULT_OUT = HERE / "figures"
OUT_BASE = "fig-e13-vram"

# Brand palette (repo brand colors; matches the sibling analysis figures)
TEAL_DARK = "#05668D"
TEAL = "#028090"
AMBER = "#F0A202"
BG = "#E8F6F3"
RED = "#C1361D"
GREY = "#9AA7AD"

THRESHOLDS = [
    (0, "laptop iGPU (0 GB)"),
    (4, "4 GB consumer"),
    (8, "8 GB consumer"),
    (24, "24 GB workstation"),
]


def as_float(v: str) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def demo_rows() -> list[dict[str, str]]:
    rng = random.Random(13)
    rows: list[dict[str, str]] = []
    # provisioned: mostly the 16 GB baseline, a few larger classes
    fc = [16] * 22 + [24, 32, 48, 16, 16, 8]
    mins = {0: "16", 3: "8", 4: "24", 10: "12"}  # a handful of documented minima (demo)
    for i in range(len(fc)):
        svc = f"demo-service-{i:02d}"
        min_v = str(mins.get(i, ""))
        rows.append({
            "service": svc,
            "gpu_class": "fc.gpu.tesla.1",
            "fc_vram_gb": str(fc[i]),
            "min_vram_gb": min_v,
            "kind": "minimum" if min_v else "tested",
            "source": "demo synthetic data" if min_v else "",
            "confidence": "demo" if min_v else "",
        })
    for i in range(4):
        rows.append({"service": f"demo-cpu-{i}", "gpu_class": "", "fc_vram_gb": "",
                     "min_vram_gb": "", "kind": "cpu", "source": "", "confidence": ""})
    return rows


def count_above(vals: list[float], t: float) -> int:
    return sum(1 for v in vals if v > t)


def plot(rows: list[dict[str, str]], out: Path) -> None:
    # GPU-provisioned bars: has a provisioned VRAM and is not CPU-only.
    provisioned = [(r, as_float(r.get("fc_vram_gb") or ""))
                   for r in rows if (r.get("fc_vram_gb") or "") != "" and (r.get("kind") or "") != "cpu"]
    provisioned = [(r, v) for r, v in provisioned if v is not None]

    # best-known minimum per service, split by provenance for styling.
    est: dict[str, tuple[float, str]] = {}
    for r in rows:
        if (r.get("kind") or "") in ("minimum", "inferred") and (r.get("min_vram_gb") or "") != "":
            v = as_float(r["min_vram_gb"])
            if v is not None:
                est[r["service"]] = (v, r["kind"])

    cpu_n = sum(1 for r in rows if (r.get("kind") or "") == "cpu" or (r.get("fc_vram_gb") or "") == "")
    total = len(rows)

    provisioned.sort(key=lambda rv: rv[1])  # ascending -> heaviest drawn on top
    labels = [r["service"].removesuffix("-server") for r, _ in provisioned]
    fc_vals = [v for _, v in provisioned]
    min_vals = [v for v, k in est.values() if k == "minimum"]
    est_vals = [v for v, _ in est.values()]

    fig, ax = plt.subplots(figsize=(7, max(5.6, 0.2 * len(provisioned) + 1.6)))
    fig.patch.set_facecolor("white")

    y = list(range(len(provisioned)))
    ax.barh(y, fc_vals, height=0.5, color=TEAL, alpha=0.85, edgecolor="white",
            linewidth=0.5, zorder=3, label="FC-provisioned GPU")

    # hardware thresholds (4 / 8 / 24 GB): red dashed lines + top labels.
    # Right-align "4 GB" (extends left of its line) and left-align "8 GB"
    # (extends right) so the two closely-spaced labels never collide.
    aligns = ["right", "left", "center"]
    for (t, label), ha in zip(THRESHOLDS[1:], aligns):
        ax.axvline(t, color=RED, ls="--", lw=1.1, alpha=0.55, zorder=2)
        dx = -0.35 if ha == "right" else 0.35 if ha == "left" else 0
        ax.text(t + dx, len(provisioned) - 0.30, f"{t} GB", ha=ha, va="bottom",
                fontsize=6.5, color=RED, clip_on=False)

    # best-known minimum markers (documented = solid, inferred = hollow)
    for i, (r, _) in enumerate(provisioned):
        hit = est.get(r["service"])
        if hit is None:
            continue
        v, kind = hit
        if kind == "minimum":
            ax.scatter([v], [i], marker="D", s=44, color=AMBER, zorder=5,
                       edgecolors="white", linewidths=0.6)
        else:
            ax.scatter([v], [i], marker="o", s=44, facecolors="none",
                       edgecolors=AMBER, linewidths=1.5, zorder=5)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_ylim(-0.55, len(provisioned) - 0.45)
    ax.set_xlim(0, max(fc_vals) * 1.10)
    ax.xaxis.set_major_locator(mticker.MultipleLocator(8))
    ax.xaxis.set_minor_locator(mticker.MultipleLocator(4))
    ax.set_xlabel("VRAM (GB)", fontsize=11)
    ax.set_title("Fleet GPU VRAM vs hardware thresholds", color=TEAL_DARK,
                 fontsize=13, fontweight="bold", loc="left", pad=24)
    ax.grid(axis="x", color="white", lw=1, alpha=0.6, zorder=0)
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GREY)

    c8 = count_above(est_vals, 8)
    c24 = count_above(est_vals, 24)
    handles = [
        Patch(facecolor=TEAL, alpha=0.85, edgecolor="white",
              label="FC-provisioned GPU"),
        Line2D([], [], linestyle="", marker="D", markersize=7, color=AMBER,
               markerfacecolor=AMBER, markeredgecolor="white",
               label="documented minimum"),
        Line2D([], [], linestyle="", marker="o", markersize=7, color=AMBER,
               markerfacecolor="none", markeredgewidth=1.5,
               label="inferred estimate (low confidence)"),
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=8, frameon=False,
              title=f"needs > 8 GB: {c8}  ·  needs > 24 GB: {c24}",
              title_fontsize=8)

    fig.suptitle("Compute barrier: the fleet cannot run on laptop / consumer / workstation GPUs",
                 color=TEAL_DARK, fontsize=14, fontweight="bold", y=1.03)

    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        target = out / f"{OUT_BASE}.{ext}"
        fig.savefig(target, dpi=150, bbox_inches="tight", facecolor="white")
        print(f"wrote {target}")
    plt.close(fig)

    print(f"\nfleet: {total} services ({cpu_n} CPU/no-gpuConfig, {len(provisioned)} GPU-provisioned)")
    for t, label in THRESHOLDS[1:]:
        print(f"  provisioned > {t:2d} GB: {count_above(fc_vals, t)}")
    print(f"  documented minimums: {len(min_vals)}  ·  inferred estimates: {len(est_vals) - len(min_vals)}")
    if est_vals:
        for t, label in THRESHOLDS[1:]:
            print(f"    best-known VRAM > {t:2d} GB: {count_above(est_vals, t)}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Compute barrier: plot services vs VRAM")
    ap.add_argument("--csv", default=str(DEFAULT_CSV))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--demo", action="store_true", help="plot synthetic data (no CSV needed)")
    args = ap.parse_args()

    csv_path = Path(args.csv)
    if args.demo:
        rows = demo_rows()
    elif csv_path.is_file():
        rows = load_rows(csv_path)
    else:
        print(f"ERROR: {csv_path} not found; run collect_vram.py first or pass --demo", file=sys.stderr)
        return 1

    plot(rows, Path(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
