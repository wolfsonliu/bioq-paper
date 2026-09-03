#!/usr/bin/env python3
"""rfantibody — per-target design funnel barplot (one PDF).

Draws the design funnel of every target side by side as a vertical grouped bar
chart: x = target, 5 bars = backbones / MPNN seqs / RF2 scored / pAE < 10 /
pAE < 10 & RMSD < 2 Å (the last bar is exactly the paper's "Ca RMSD < 2 Å and
pAE Interaction < 10" combined criterion, i.e. design passing *both* filters).
The y-axis is log-scaled (the funnel spans ~37 to ~8000 designs, i.e. a couple
of orders of magnitude) so the small "passed" counts stay legible.

Styled to ``docs/plotting-style-guide.md`` (Arial, brand palette, tinted panel,
soft grid, dropped top/right spines, left-aligned bold title); tight-cropped PDF
width stays below 16 cm.

    python3 plot_funnel.py                       # all targets in one PDF
    python3 plot_funnel.py --target HIV_Env,TcdB # a subset
    python3 plot_funnel.py --out /tmp/rfantibody.pdf     # custom output path
"""
from __future__ import annotations

import argparse
import json
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

BLUE = "#2E86AB"  # brand categorical extension (docs/plotting-style-guide.md §1.1)

FUNNEL_KEYS = ["rfdiffusion_backbones", "mpnn_sequences",
               "rf2_scored", "pae_pass", "passed_filter"]
FUNNEL_LABELS = ["backbones", "MPNN seqs", "RF2 scored",
                 "pAE<10", "pAE<10 & RMSD<2\u00c5"]
# Pipeline volume = cool teal->blue ramp; first filter pass = GREEN; the final
# combined pass (key surviving result) = AMBER highlight.
FUNNEL_COLORS = [P.TEAL_DARK, P.TEAL, BLUE, P.GREEN, P.AMBER]


def _label(target: str) -> str:
    return TARGET_LABELS.get(target, target)


def _load_summary() -> list[dict]:
    path = DATA / "campaign_summary.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _style(ax, title: str) -> None:
    ax.set_facecolor(P.BG)
    ax.grid(True, alpha=0.3, axis="y", which="both", zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(P.GREY)
    if title:
        ax.set_title(title, color=P.TEAL_DARK, fontsize=7.5,
                     fontweight="bold", loc="left")


def _draw_funnel_grouped(ax, valid: list[dict], title: str) -> None:
    labels = [_label(f["target"]) for f in valid]
    x = np.arange(len(valid))
    width = 0.16
    offsets = [-2 * width, -1 * width, 0.0, 1 * width, 2 * width]

    all_vals: list[int] = []
    for j, (key, color) in enumerate(zip(FUNNEL_KEYS, FUNNEL_COLORS)):
        vals = [int((f["stages"].get(key)) or 0) for f in valid]
        all_vals.extend(vals)
        ax.bar(x + offsets[j], vals, width, color=color,
               label=FUNNEL_LABELS[j], edgecolor="white", linewidth=0.4, zorder=3)

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=5.5)
    ax.set_yscale("log")
    ax.set_ylim(max(10, min(all_vals) * 0.5), max(all_vals) * 2.0)
    ax.set_ylabel("count (log scale)", fontsize=6.5)
    _style(ax, title)
    ax.legend(fontsize=6, frameon=False, ncol=5, loc="upper center",
              columnspacing=0.9, handletextpad=0.4)


def build_figure(valid: list[dict]) -> plt.Figure:
    fig = plt.figure(figsize=(6.2, 2.8), facecolor="white")
    ax = fig.add_subplot(1, 1, 1)
    _draw_funnel_grouped(ax, valid, "design funnel per target")
    fig.suptitle("RFantibody de novo design via bioq \u2014 design funnel "
                 "(no local GPU; 3 bioq calls per target)",
                 color=P.TEAL_DARK, fontsize=10, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93], pad=0.6, h_pad=0.7, w_pad=0.7)
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--target", "--targets",
                    help="comma-separated target keys (default: all under data/)")
    ap.add_argument("--out", default=str(FIGURES / "rfantibody_funnel.pdf"),
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
