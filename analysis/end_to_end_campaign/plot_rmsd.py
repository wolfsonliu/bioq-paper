#!/usr/bin/env python3
"""rfantibody — 3x3 grid of framework-aligned CDR RMSD histograms (one PDF).

Mirror of ``plot_pae.py`` for the second half of the paper's in-silico filter
(``Ca RMSD < 2 Å and pAE Interaction < 10``): one histogram per design target of
``framework_aligned_cdr_rmsd`` (self-consistency RMSD, design vs RF2-predicted),
green = pass (< 2 Å), grey = fail, amber dashed threshold at 2 Å. All nine panels
share a single binning (``[0, 24)`` in 1 Å steps, wide enough for the scFv tail)
so they are directly comparable. Unused grid cells (e.g. a ``--target`` subset)
are left blank.

Reads ``data/<target>/designs.csv`` (field ``cfg.FILTER["rmsd_field"]``, threshold
``cfg.FILTER["rmsd_max"]``). Styled to ``docs/plotting-style-guide.md``;
tight-cropped PDF width stays below 16 cm.

    python3 plot_rmsd.py                       # all nine targets in one PDF
    python3 plot_rmsd.py --target HIV_Env,TcdB # a subset (blank cells hidden)
    python3 plot_rmsd.py --out /tmp/rfantibody.pdf     # custom output path
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 7,
        "axes.titlesize": 7.5,
        "axes.labelsize": 6.5,
        "xtick.labelsize": 5.5,
        "ytick.labelsize": 5.5,
        "legend.fontsize": 5.5,
        "figure.titlesize": 11,
    }
)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # for the shared brand palette (palette.py)
import config as cfg
import palette as P

DATA = HERE / "data"
FIGURES = HERE / "figures"

TARGET_LABELS = {
    "HIV_Env": "HIV Env",
    "IL7R_alpha": "IL-7R\u03b1",
    "Influenza_HA": "Influenza HA",
    "RSV_Site_I": "RSV-F Site I",
    "RSV_Site_III": "RSV-F Site III",
    "SARS_CoV2_RBD": "SARS-CoV-2 RBD",
    "TcdB": "TcdB",
    "TcdB_scFv_combinatorial": "TcdB scFv comb.",
    "TcdB_scFv_unique": "TcdB scFv unique",
}

# Shared x-range for every panel. The VHH targets cluster below ~7 Å while the
# combinatorial scFv tails to ~22.6 Å, so the range extends far enough to show
# that tail while keeping every panel on one comparable scale. The threshold 2 Å
# lands on a bin edge, giving a clean pass/fail split.
RMSD_BIN_EDGES = np.arange(0.0, 24.0, 1.0)


def _label(target: str) -> str:
    return TARGET_LABELS.get(target, target)


def _load_summary() -> list[dict]:
    path = DATA / "campaign_summary.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _load_rmsd(target: str) -> list[float]:
    field = cfg.FILTER["rmsd_field"]
    out: list[float] = []
    path = DATA / target / "designs.csv"
    if not path.exists():
        return out
    with path.open() as fh:
        for row in csv.DictReader(fh):
            try:
                v = float(row[field])
            except (KeyError, ValueError, TypeError):
                continue
            if math.isfinite(v):
                out.append(v)
    return out


def _style(ax, title: str) -> None:
    ax.set_facecolor(P.BG)
    ax.grid(True, alpha=0.3, axis="y", zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(P.GREY)
    if title:
        ax.set_title(title, color=P.TEAL_DARK, fontsize=7.5,
                     fontweight="bold", loc="left")


def _draw_rmsd_hist(ax, rmsd: list[float], thr: float, title: str) -> None:
    finite = [v for v in rmsd if math.isfinite(v)]
    if not finite:
        ax.set_facecolor(P.BG)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(P.GREY)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.text(0.5, 0.5, "no RMSD data", ha="center", va="center",
                color=P.GREY, fontsize=6, transform=ax.transAxes)
        return

    passv = [v for v in finite if v < thr]
    failv = [v for v in finite if v >= thr]
    npass = len(passv)
    ax.hist(passv, bins=RMSD_BIN_EDGES, color=P.GREEN, rwidth=0.9, zorder=3)
    ax.hist(failv, bins=RMSD_BIN_EDGES, color=P.GREY, rwidth=0.9, zorder=3)
    ax.axvline(thr, ls="--", color=P.AMBER, lw=1.2, zorder=4)
    ax.set_xlabel("framework-aligned CDR RMSD (\u00c5)", fontsize=6)
    ax.set_ylabel("designs", fontsize=6)
    # Two-line title (target / pass count) so it fits the narrow columns.
    _style(ax, f"{title}\n({npass}/{len(finite)} < {thr:g})")


def build_figure(valid: list[dict]) -> plt.Figure:
    # 3 rows x 3 columns, top to bottom in reading order; extra cells blank.
    fig = plt.figure(figsize=(6.2, 5.2), facecolor="white")
    gs = fig.add_gridspec(3, 3)

    thr = cfg.FILTER["rmsd_max"]
    for i, f in enumerate(valid):
        if i >= 9:
            break
        r, c = divmod(i, 3)
        ax = fig.add_subplot(gs[r, c])
        _draw_rmsd_hist(ax, _load_rmsd(f["target"]), thr, _label(f["target"]))

    for i in range(len(valid), 9):
        r, c = divmod(i, 3)
        ax = fig.add_subplot(gs[r, c])
        ax.axis("off")

    fig.suptitle("RFantibody de novo design via bioq \u2014 framework-aligned "
                 "CDR RMSD\ndistribution (no local GPU; 3 bioq calls per target)",
                 color=P.TEAL_DARK, fontsize=10, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.94], pad=0.6, h_pad=0.9, w_pad=0.8)
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--target", "--targets",
                    help="comma-separated target keys (default: all under data/)")
    ap.add_argument("--out", default=str(FIGURES / "rfantibody_rmsd.pdf"),
                    help="output PDF path")
    args = ap.parse_args()

    summary = _load_summary()
    valid = [f for f in summary if f.get("stages")]
    valid.sort(key=lambda f: f["target"])

    if args.target:
        keep = {t.strip() for t in args.target.split(",") if t.strip()}
        missing = keep - {f["target"] for f in valid}
        valid = [f for f in valid if f["target"] in keep]
        if missing:
            print(f"warning: targets not in campaign_summary.json: "
                  f"{', '.join(sorted(missing))}")

    if not valid:
        print("No scorable targets found (run analyze.py first).")
        sys.exit(1)

    fig = build_figure(valid)

    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight", pad_inches=0.05, format="pdf")
    try:
        print(f"Wrote {out.relative_to(HERE)}")
    except ValueError:
        print(f"Wrote {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
