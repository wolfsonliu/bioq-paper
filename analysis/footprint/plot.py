#!/usr/bin/env python3
"""Footprint sub-analysis figure — image footprint vs the bioq thin client (offline plot).

Reads ``data/footprint.csv`` (produced by ``collect_footprint.py``) and renders
``figures/footprint.pdf``. Per ``docs/plotting-style-guide.md`` §6, plotting
is separate from collection: this script only reads committed data and never
touches Docker or a venv, so it can re-draw the figure without re-measuring
anything.

Usage:
    python3 plot.py                                    # data/ -> figures/
    python3 plot.py --data-dir path/to/data             # different inputs
    python3 plot.py --out-dir path/to/figures           # different outputs
    python3 plot.py --dpi 200                           # override resolution

Requires: matplotlib (``uv run --with matplotlib python plot.py``).
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

HERE = Path(__file__).resolve().parent

# --- Brand palette (docs/plotting-style-guide.md §1.1) ---
TEAL_DARK = "#05668D"
TEAL      = "#028090"
GREEN     = "#02C39A"
AMBER     = "#F0A202"
BG        = "#E8F6F3"
RED       = "#C1361D"
GREY      = "#9AA7AD"
PURPLE    = "#7B2D8E"
BLUE      = "#2E86AB"
ORANGE    = "#E76F51"


def style_axes(ax, title: str | None = None, *, grid_axis: str | None = None,
               grid_which: str = "major") -> None:
    """Apply the signature panel grammar (plotting-style-guide.md §3)."""
    ax.set_facecolor(BG)
    ax.grid(True, alpha=0.3, axis=grid_axis or "both", which=grid_which)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GREY)
    if title:
        ax.set_title(title, color=TEAL_DARK, fontsize=13, fontweight="bold",
                     loc="left")


def _fmt_size(mb: float) -> str:
    """Human-readable size label (MB below 1 GB, GB beyond; 1 GB = 1000 MB)."""
    if mb >= 1000:
        return f"{mb / 1000:.1f} GB"
    if mb >= 100:
        return f"{mb:.0f} MB"
    return f"{mb:.1f} MB"


def load_footprint(data_dir: Path) -> tuple[list[tuple[str, float]], int, int]:
    """Read ``footprint.csv`` -> (measured [(label, mb)], n_services, n_missing)."""
    data_file = data_dir / "footprint.csv"
    if not data_file.is_file():
        raise SystemExit(f"required input not found: {data_file} "
                         "(run collect_footprint.py first)")
    rows = list(csv.DictReader(
        data_file.open(newline="", encoding="utf-8")))

    n_services = sum(1 for r in rows if r["service"] != "bioq (thin client)")
    n_missing = sum(1 for r in rows if r["status"] == "not_built_locally")
    measured = [(r["service"].replace("-server", ""), float(r["image_size_mb"]))
                for r in rows if r["image_size_mb"] != ""]
    return measured, n_services, n_missing


def plot_footprint(measured: list[tuple[str, float]], n_services: int,
                   n_missing: int, out: Path, dpi: int = 150) -> None:
    """Render the footprint figure: log-scale image-size bars vs the bioq thin client."""
    if not measured:
        return
    measured.sort(key=lambda x: x[1])
    labels = [m[0] for m in measured]
    vals = [m[1] for m in measured]
    is_bioq = [lab.startswith("bioq") for lab in labels]

    # Height-proportional rows (guide §8): keeps ~34 tick labels readable.
    fig, ax = plt.subplots(figsize=(7, max(4.5, 0.2 * len(measured) + 1.6)))

    # bioq client = key data (AMBER); service images = primary series (TEAL).
    ax.barh(labels, vals,
            color=[AMBER if b else TEAL for b in is_bioq],
            alpha=0.85, edgecolor="white", linewidth=0.5)

    # Per-bar value labels (log scale needs explicit annotations).
    for y, (v, b) in enumerate(zip(vals, is_bioq)):
        ax.text(v * 1.05, y, _fmt_size(v), va="center", ha="left",
                fontsize=8, color=TEAL_DARK,
                fontweight="bold" if b else "normal")

    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: _fmt_size(x)))
    ax.set_xlabel("On-disk size (log scale)", fontsize=11)
    ax.margins(x=0.18)
    style_axes(ax, "Image footprint — bioq client vs locally-built service images",
               grid_axis="x", grid_which="both")

    # Caption (grey) below the axes — reserved via tight_layout(rect=…).
    caption = (f"{n_missing} of {n_services} service images not built locally — "
               "fleet total is a partial sum")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.text(0.0, 0.012, caption, ha="left", va="bottom",
             fontsize=8, color=GREY)

    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    try:
        print(f"wrote {out.relative_to(HERE)}")
    except ValueError:
        print(f"wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default=str(HERE / "data"),
                    help="dir with footprint.csv (default: footprint/data/)")
    ap.add_argument("--out-dir", default=str(HERE / "figures"),
                    help="output dir for the PDF (default: footprint/figures/)")
    ap.add_argument("--dpi", type=int, default=150,
                    help="figure resolution (default: 150)")
    args = ap.parse_args()

    data_dir = Path(args.data_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()

    measured, n_services, n_missing = load_footprint(data_dir)
    n_svc = sum(1 for lab, _ in measured if not lab.startswith("bioq"))
    print(f"reading {data_dir / 'footprint.csv'}")
    print(f"  services: {n_services}   measured: {n_svc}   "
          f"not built locally: {n_missing}")

    plot_footprint(measured, n_services, n_missing,
                   out_dir / "footprint.pdf", args.dpi)


if __name__ == "__main__":
    main()
