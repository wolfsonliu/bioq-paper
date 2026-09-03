#!/usr/bin/env python3
"""rfantibody — single multi-panel supplementary figure (one PDF, <=16 cm wide).

``plot.py`` renders the campaign overview and then *one separate figure per
target* (``rfantibody_campaign.pdf`` + 9 ``rfantibody_<target>.pdf``). Two
dozen separate PDFs are awkward to tile into a paper's supplementary section, so
this script recomposes **every analysis panel into one tall figure**:

    (a) per-target in-silico pass fraction      (sequence-level, pAE-only vs pAE+RMSD)
    (b) combined design funnel across targets
    (c) backbone-level success rate vs the RFantibody paper

followed by **one row per target** (9 rows) with four panels each:

    target funnel   |   interaction-pAE distribution   |   filter contribution   |   vs paper

The figure is styled to ``docs/plotting-style-guide.md`` (Arial, brand palette,
tinted panels, soft grid, dropped top/right spines, left-aligned bold titles) and
its tight-cropped PDF width stays below 16 cm (160 mm).

Reads ``data/campaign_summary.json`` (+ ``data/<target>/designs.csv`` for the pAE
distribution, + ``rfantibody_paper_baseline.csv`` for the "vs paper"
panel) and writes one editable vector PDF. Offline; separate from collection.

    python3 plot_supplementary.py                       # all targets in one PDF
    python3 plot_supplementary.py --target HIV_Env,TcdB # a subset, still one PDF
    python3 plot_supplementary.py --out /tmp/rfantibody.pdf     # custom output path
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
# Embed fonts as TrueType (not Type 3) so the PDF text stays editable in
# Illustrator / Inkscape / PowerPoint.
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt
import numpy as np

# Arial for all text, sized so the tight-cropped PDF width lands below 16 cm —
# mirroring the canonical throughput-scaling figure (2 6.25-inch-wide 3x2 grid).
plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 7,
        "axes.titlesize": 8,
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
PAPER_CSV = HERE / "rfantibody_paper_baseline.csv"

# Natural-language labels for the figure (the raw target keys stay the canonical
# identifiers in data/ and campaign_summary.json; these are only for display).
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

FUNNEL_KEYS = ["rfdiffusion_backbones", "mpnn_sequences",
               "rf2_scored", "passed_filter"]
FUNNEL_LABELS = ["backbones", "MPNN\nseqs", "RF2\nscored", "passed\nfilter"]
# Sequential-ish brand ramp: deep -> main -> accent -> highlighted key number.
FUNNEL_COLORS = [P.TEAL_DARK, P.TEAL, P.GREEN, P.AMBER]

# Shared x-range for every per-target pAE histogram so the 9 panels are directly
# comparable (observed interaction_pae spans ~2.4..24 across the campaign).
PAE_BIN_EDGES = np.arange(2.0, 26.0, 1.0)


def _label(target: str) -> str:
    return TARGET_LABELS.get(target, target)


def _count_label(v) -> str:
    """Compact thousands for funnel bar labels (they must fit a ~1.2 in panel)."""
    if v >= 1000:
        return f"{v / 1000:.1f}k"
    return f"{v}"


def _load_summary() -> list[dict]:
    path = DATA / "campaign_summary.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _load_pae(target: str) -> list[float]:
    """Finite ``interaction_pae`` values for one target (from designs.csv)."""
    field = cfg.FILTER["field"]
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


def _load_paper_baseline() -> dict:
    """{target: rf2_success_hotspot1_pct (float) or None}, deduped by target."""
    out: dict = {}
    if not PAPER_CSV.exists():
        return out
    with PAPER_CSV.open() as fh:
        for row in csv.DictReader(fh):
            t = row.get("target")
            if not t or t in out:
                continue
            v = row.get("rf2_success_hotspot1_pct", "").strip()
            try:
                out[t] = float(v)
            except (ValueError, TypeError):
                out[t] = None
    return out


def _ours_pct(funnel: dict):
    """Our backbone success rate, in % (best-of-8, paper convention)."""
    v = funnel.get("backbone_pass_fraction")
    return None if v is None else v * 100.0


# ---------------------------------------------------------------------------
# Panel grammar (§3 of docs/plotting-style-guide.md)
# ---------------------------------------------------------------------------
def _style(ax, title: str, grid_axis: str) -> None:
    ax.set_facecolor(P.BG)
    ax.grid(True, alpha=0.3, axis=grid_axis, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(P.GREY)
    if title:
        ax.set_title(title, color=P.TEAL_DARK, fontsize=8,
                     fontweight="bold", loc="left")


def _empty(ax, msg: str) -> None:
    ax.set_facecolor(P.BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(P.GREY)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(0.5, 0.5, msg, ha="center", va="center", color=P.GREY,
            fontsize=6, transform=ax.transAxes)


# ---------------------------------------------------------------------------
# Drawing primitives
# ---------------------------------------------------------------------------
def _draw_funnel(ax, stages: dict, title: str) -> None:
    vals = [int(stages.get(k) or 0) for k in FUNNEL_KEYS]
    y = list(range(len(vals)))[::-1]
    ax.barh(y, vals, color=FUNNEL_COLORS, height=0.72,
            edgecolor="white", linewidth=0.5, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(FUNNEL_LABELS, fontsize=5.5)
    mx = max(vals) if vals else 1
    for i, v in zip(y, vals):
        ax.text(v, i, f" {_count_label(v)}", va="center", ha="left",
                fontsize=5.5, color=P.TEAL_DARK, fontweight="bold")
    ax.set_xlim(0, mx * 1.40)  # headroom keeps the count label inside the axes
    _style(ax, title, grid_axis="x")


def _draw_pae_hist(ax, pae: list[float], thr: float, title: str) -> None:
    finite = [v for v in pae if math.isfinite(v)]
    if not finite:
        _empty(ax, "no pAE data")
        return
    passv = [v for v in finite if v < thr]
    failv = [v for v in finite if v >= thr]
    npass = len(passv)
    ax.hist(passv, bins=PAE_BIN_EDGES, color=P.GREEN, rwidth=0.9, zorder=3)
    ax.hist(failv, bins=PAE_BIN_EDGES, color=P.GREY, rwidth=0.9, zorder=3)
    ax.axvline(thr, ls="--", color=P.AMBER, lw=1.2, zorder=4)
    ax.set_xlabel("interaction pAE", fontsize=6)
    ax.set_ylabel("designs", fontsize=6)
    _style(ax, f"{title}  ({npass}/{len(finite)} < {thr:g})", grid_axis="y")


def _draw_pass_frac(ax, funnel: dict, title: str) -> None:
    pae = funnel.get("pae_pass_fraction")
    full = funnel.get("in_silico_pass_fraction")
    labels: list[str] = []
    vals: list[float] = []
    cols: list[str] = []
    if pae is not None:
        labels.append("pAE")
        vals.append(pae)
        cols.append(P.GREEN)
    if full is not None:
        labels.append("pAE+RMSD")
        vals.append(full)
        cols.append(P.TEAL)
    if not vals:
        _empty(ax, "no fractions")
        return
    x = range(len(vals))
    ax.bar(list(x), vals, color=cols, width=0.60,
           edgecolor="white", linewidth=0.5, zorder=3)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=5.5)
    ax.set_ylabel("pass fraction", fontsize=6)
    ax.set_ylim(0, max(vals + [0.1]) * 1.35)
    for xi, v in zip(x, vals):
        ax.text(xi, v, f" {v:.3f}", ha="center", va="bottom",
                fontsize=5.5, color=P.TEAL_DARK, fontweight="bold")
    _style(ax, title, grid_axis="y")


def _draw_vs_paper(ax, names: list[str], ours_pct: list, paper_pct: list,
                   title: str, legend: bool = False) -> None:
    pairs = [(t, o, p) for t, o, p in zip(names, ours_pct, paper_pct)
             if p is not None and o is not None]
    if not pairs:
        _empty(ax, "no paper\nbaseline")
        return

    labels = [p[0] for p in pairs]
    ours = [p[1] for p in pairs]
    paper = [p[2] for p in pairs]
    y = list(range(len(pairs)))[::-1]
    h = 0.34
    ax.barh([i + h / 2 for i in y], ours, h, color=P.TEAL,
            label="this work (bioq)", edgecolor="white", linewidth=0.5, zorder=3)
    ax.barh([i - h / 2 for i in y], paper, h, color=P.GREY,
            label="paper (RF2)", edgecolor="white", linewidth=0.5, zorder=3)
    for i, (o, p) in zip(y, zip(ours, paper)):
        ax.text(o, i + h / 2, f" {o:.1f}%", va="center", ha="left",
                fontsize=5.5, color=P.TEAL_DARK, fontweight="bold")
        ax.text(p, i - h / 2, f" {p:.1f}%", va="center", ha="left",
                fontsize=5.5, color=P.TEAL_DARK)
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=5.5)
    ax.set_xlabel("backbone success (%)", fontsize=6)
    ax.set_xlim(0, max(ours + paper + [1]) * 1.50)  # room for the % callout labels
    if legend:
        ax.legend(fontsize=5, frameon=False, ncol=1, loc="upper right")
    _style(ax, title, grid_axis="x")


def _draw_overview_pass(ax, valid: list[dict], title: str) -> None:
    labels = [_label(f["target"]) for f in valid]
    pae = [f.get("pae_pass_fraction") or 0 for f in valid]
    full = [f.get("in_silico_pass_fraction") or 0 for f in valid]
    x = range(len(valid))
    w = 0.36
    ax.bar([i - w / 2 for i in x], pae, w, color=P.GREEN,
           label="pAE < 10", edgecolor="white", linewidth=0.4, zorder=3)
    ax.bar([i + w / 2 for i in x], full, w, color=P.TEAL,
           label="pAE < 10 & RMSD < 2\u00c5", edgecolor="white", linewidth=0.4, zorder=3)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=5.5)
    ax.set_ylabel("pass fraction", fontsize=6)
    ax.set_ylim(0, max(pae + full + [0.1]) * 1.3)
    ax.legend(fontsize=5.5, frameon=False, ncol=1, loc="upper left")
    _style(ax, title, grid_axis="y")


# ---------------------------------------------------------------------------
# Figure assembly
# ---------------------------------------------------------------------------
def build_figure(valid: list[dict], paper: dict) -> plt.Figure:
    n = len(valid)
    nrows = 1 + n
    unit = 1.16  # inches per detail row; overview row is 1.7x that
    fig = plt.figure(figsize=(6.2, unit * (1.7 + n)), facecolor="white")
    gs = fig.add_gridspec(nrows, 4,
                          width_ratios=[1.30, 1.20, 0.85, 0.85],
                          height_ratios=[1.7] + [1.0] * n)

    # ---- Overview row (spans all four columns) ---------------------------
    ax_ov_pass = fig.add_subplot(gs[0, 0:2])
    ax_ov_funnel = fig.add_subplot(gs[0, 2])
    ax_ov_vs = fig.add_subplot(gs[0, 3])

    names = [f["target"] for f in valid]
    labels = [_label(t) for t in names]

    _draw_overview_pass(ax_ov_pass, valid,
                        "(a) per-target pass fraction (sequence-level)")
    combined = {k: sum(f["stages"].get(k) or 0 for f in valid)
                for k in FUNNEL_KEYS}
    _draw_funnel(ax_ov_funnel, combined, "(b) combined funnel")
    _draw_vs_paper(ax_ov_vs, labels,
                   [_ours_pct(f) for f in valid],
                   [paper.get(t) for t in names],
                   "(c) vs paper", legend=True)

    # ---- One row per target ----------------------------------------------
    thr = cfg.FILTER["threshold"]
    for r, f in enumerate(valid, start=1):
        target = f["target"]
        label = _label(target)
        stages = f.get("stages", {})
        pae = _load_pae(target)

        ax_funnel = fig.add_subplot(gs[r, 0])
        ax_hist = fig.add_subplot(gs[r, 1])
        ax_pass = fig.add_subplot(gs[r, 2])
        ax_vs = fig.add_subplot(gs[r, 3])

        _draw_funnel(ax_funnel, stages, f"{label} funnel")
        _draw_pae_hist(ax_hist, pae, thr, "pAE")
        _draw_pass_frac(ax_pass, f, "filter")
        _draw_vs_paper(ax_vs, [label], [_ours_pct(f)],
                       [paper.get(target)], "vs paper")

    fig.suptitle("RFantibody de novo design via bioq \u2014 in-silico funnel\n"
                 "(no local GPU; 3 bioq calls per target)",
                 color=P.TEAL_DARK, fontsize=10, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.985], pad=0.6, h_pad=0.7, w_pad=0.7)
    return fig


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--target", "--targets",
                    help="comma-separated target keys (default: all under data/)")
    ap.add_argument("--out", default=str(FIGURES / "rfantibody_supplementary.pdf"),
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

    paper = _load_paper_baseline()
    fig = build_figure(valid, paper)

    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    # pad_inches=0.05 trims the default 0.1" tight-bbox border so the final PDF
    # stays under the 16 cm (≈6.3 in) width budget for the manuscript.
    fig.savefig(out, dpi=150, bbox_inches="tight", pad_inches=0.05, format="pdf")
    try:
        print(f"Wrote {out.relative_to(HERE)}")
    except ValueError:
        print(f"Wrote {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
