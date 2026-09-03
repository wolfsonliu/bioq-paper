#!/usr/bin/env python3
"""rfantibody — figure.  ***Offline; separate from collection.***

Renders the in-silico design funnel from ``analyze.py`` output and compares the
per-backbone success rate against the RFantibody paper's reported RF2 rates
(``./rfantibody_paper_baseline.csv``).

    python3 plot.py                     # campaign overview + one figure per target
    python3 plot.py --target HIV_Env    # only the HIV_Env detailed figure
    python3 plot.py --campaign-only     # only the campaign overview

Reads ``data/campaign_summary.json`` (+ ``data/<target>/designs.csv`` for the
PAE distribution, + ``./rfantibody_paper_baseline.csv`` for the "vs
paper" panel) and writes editable PDF(s) under ``figures/``, using the shared
brand palette.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
# Embed fonts as TrueType (not Type 3) so the PDF text stays editable in
# Illustrator / Inkscape / PowerPoint.
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # for palette
import config as cfg
import palette as P

DATA = HERE / "data"
FIGURES = HERE / "figures"
PAPER_CSV = HERE / "rfantibody_paper_baseline.csv"

FUNNEL_KEYS = ["rfdiffusion_backbones", "mpnn_sequences",
               "rf2_scored", "passed_filter"]
FUNNEL_LABELS = ["RFdiffusion\nbackbones", "MPNN\nsequences",
                 "RF2\nscored", "passed\nfilter"]


def _load_summary() -> list[dict]:
    path = DATA / "campaign_summary.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _load_pae(target: str) -> list[float]:
    field = cfg.FILTER["field"]
    out: list[float] = []
    path = DATA / target / "designs.csv"
    if not path.exists():
        return out
    with path.open() as fh:
        for row in csv.DictReader(fh):
            try:
                out.append(float(row[field]))
            except (KeyError, ValueError, TypeError):
                pass
    return out


def _load_paper_baseline() -> dict:
    """{target: rf2_success_hotspot1_pct (float) or None}, deduped by target.

    The paper's rate is the fine-tuned-RF2 success rate at hotspot proportion
    = 1 (per-backbone, best-of-8 sequences — same convention as analyze.py's
    ``backbone_pass_fraction``).
    """
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


def _style_axes(ax, title: str) -> None:
    ax.set_title(title, color=P.TEAL_DARK, fontweight="bold", loc="left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def _draw_funnel(ax, stages: dict) -> None:
    vals = [stages.get(k) or 0 for k in FUNNEL_KEYS]
    colors = [P.TEAL_DARK, P.TEAL, "#00A896", P.GREEN]
    y = range(len(vals))[::-1]
    ax.barh([i for i in y], vals, color=colors)
    ax.set_yticks([i for i in y])
    ax.set_yticklabels(FUNNEL_LABELS, fontsize=9)
    for i, v in zip(y, vals):
        ax.text(v, i, f" {v:,}", va="center", fontsize=10,
                color=P.TEAL_DARK, fontweight="bold")
    _style_axes(ax, "in-silico design funnel")


def _draw_pae_hist(ax, pae: list[float], thr: float) -> None:
    if not pae:
        ax.axis("off")
        return
    npass = sum(1 for v in pae if v < thr)
    ax.hist([v for v in pae if v < thr], bins=15, color=P.GREEN,
            label=f"pass (<{thr})")
    ax.hist([v for v in pae if v >= thr], bins=15, color=P.GREY,
            label=f"fail (\u2265{thr})")
    ax.axvline(thr, ls="--", color=P.AMBER, lw=1.8)
    ax.set_xlabel(cfg.FILTER["field"], fontsize=9)
    ax.set_ylabel("designs", fontsize=9)
    ax.legend(fontsize=8, frameon=False)
    _style_axes(ax, f"{cfg.FILTER['field']} < {thr}  ({npass}/{len(pae)} pass)")


def _draw_pass_frac(ax, funnel: dict) -> None:
    pae_frac = funnel.get("pae_pass_fraction")
    full_frac = funnel.get("in_silico_pass_fraction")
    labels, vals, cols = [], [], []
    if pae_frac is not None:
        labels.append("pAE < 10\nonly")
        vals.append(pae_frac)
        cols.append(P.GREEN)
    if full_frac is not None:
        labels.append("pAE < 10\n& RMSD < 2\u00c5")
        vals.append(full_frac)
        cols.append(P.TEAL)
    if not vals:
        ax.axis("off")
        return
    ax.bar(labels, vals, color=cols)
    ax.set_ylabel("pass fraction", fontsize=9)
    ax.set_ylim(0, max(vals + [0.1]) * 1.3)
    for i, v in enumerate(vals):
        ax.text(i, v, f" {v:.3f}", ha="center", va="bottom",
                fontsize=9, color=P.TEAL_DARK, fontweight="bold")
    _style_axes(ax, "filter contribution")


def _draw_vs_paper(ax, names: list[str], ours_pct: list, paper_pct: list) -> None:
    """Grouped horizontal bars: this-work vs paper backbone success rate (%)."""
    pairs = [(t, o, p) for t, o, p in zip(names, ours_pct, paper_pct)
             if p is not None and o is not None]
    if not pairs:
        ax.axis("off")
        ax.text(0.5, 0.5, "no paper RF2 baseline\nfor these targets",
                ha="center", va="center", color=P.GREY, fontsize=10)
        return

    labels = [p[0] for p in pairs]
    ours = [p[1] for p in pairs]
    paper = [p[2] for p in pairs]
    y = range(len(pairs))[::-1]
    h = 0.36
    ax.barh([i + h / 2 for i in y], ours, h, color=P.GREEN,
            label="this work (bioq)")
    ax.barh([i - h / 2 for i in y], paper, h, color=P.TEAL,
            label="paper (RF2 hotspot=1)")
    for i, (o, p) in zip(y, zip(ours, paper)):
        ax.text(o, i + h / 2, f" {o:.1f}%", va="center", fontsize=8,
                color=P.TEAL_DARK, fontweight="bold")
        ax.text(p, i - h / 2, f" {p:.1f}%", va="center", fontsize=8,
                color=P.TEAL_DARK, fontweight="bold")
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("backbone success rate (%)", fontsize=9)
    ax.set_xlim(0, max(ours + paper + [1]) * 1.25)
    ax.legend(fontsize=8, frameon=False)
    _style_axes(ax, "vs paper (best-of-8 backbones)")


def _figure_path(name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    return FIGURES / name


def plot_campaign(summary: list[dict]) -> Path:
    valid = [f for f in summary if f.get("stages")]
    if not valid:
        fig, ax = plt.subplots(figsize=(7, 2))
        ax.text(0.5, 0.5, "no campaign analysis yet\n(run analyze.py first)",
                ha="center", va="center", color=P.GREY, fontsize=12)
        ax.axis("off")
        out = _figure_path("rfantibody_campaign.pdf")
        fig.tight_layout()
        fig.savefig(out, bbox_inches="tight")
        plt.close(fig)
        return out

    paper = _load_paper_baseline()
    n = len(valid)
    fig, (a1, a2, a3) = plt.subplots(
        1, 3, figsize=(6 + 2.2 * n, 4.4),
        gridspec_kw={"width_ratios": [n, 1.8, n]})

    # Left: per-target pass fraction (sequence-level, pAE-only vs pAE+RMSD).
    names = [f["target"] for f in valid]
    pae_fracs = [f.get("pae_pass_fraction") or 0 for f in valid]
    full_fracs = [f.get("in_silico_pass_fraction") or 0 for f in valid]
    x = range(n)
    w = 0.38
    a1.bar([i - w / 2 for i in x], pae_fracs, w, color=P.GREEN, label="pAE < 10")
    a1.bar([i + w / 2 for i in x], full_fracs, w, color=P.TEAL,
           label="pAE < 10 & RMSD < 2\u00c5")
    a1.set_xticks(list(x))
    a1.set_xticklabels(names, rotation=20, ha="right", fontsize=8)
    a1.set_ylabel("in-silico pass fraction", fontsize=9)
    a1.set_ylim(0, max(pae_fracs + full_fracs + [0.1]) * 1.3)
    a1.legend(fontsize=8, frameon=False)
    _style_axes(a1, "per-target pass fraction (sequence-level)")

    # Middle: combined funnel across all targets (sequence-level).
    combined = {k: sum(f["stages"].get(k) or 0 for f in valid)
                for k in FUNNEL_KEYS}
    _draw_funnel(a2, combined)
    a2.set_title(f"combined funnel ({n} target{'s' if n > 1 else ''})",
                 color=P.TEAL_DARK, fontweight="bold", loc="left")

    # Right: vs paper (per-backbone best-of-8 success rate).
    ours = [_ours_pct(f) for f in valid]
    paper_pct = [paper.get(f["target"]) for f in valid]
    _draw_vs_paper(a3, names, ours, paper_pct)

    fig.suptitle("RFantibody de novo design via bioq \u2014 in-silico funnel "
                 f"(no local GPU; {len(cfg.STEPS)} bioq calls)",
                 color=P.TEAL_DARK, fontsize=13, fontweight="bold")
    fig.tight_layout()
    out = _figure_path("rfantibody_campaign.pdf")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def plot_target(funnel: dict) -> Path:
    target = funnel["target"]
    stages = funnel.get("stages", {})
    pae = _load_pae(target)
    thr = cfg.FILTER["threshold"]
    paper = _load_paper_baseline()

    fig, (a1, a2, a3, a4) = plt.subplots(
        1, 4, figsize=(18, 4.2),
        gridspec_kw={"width_ratios": [1.2, 1.3, 0.8, 0.9]})
    _draw_funnel(a1, stages)
    _draw_pae_hist(a2, pae, thr)
    _draw_pass_frac(a3, funnel)
    _draw_vs_paper(a4, [target], [_ours_pct(funnel)],
                   [paper.get(target)])

    fig.suptitle(f"RFantibody de novo design via bioq \u2014 {target} "
                 f"(no local GPU; {len(cfg.STEPS)} bioq calls)",
                 color=P.TEAL_DARK, fontsize=13, fontweight="bold")
    fig.tight_layout()
    out = _figure_path(f"rfantibody_{target}.pdf")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--target", help="render only this one target's detailed figure")
    ap.add_argument("--campaign-only", action="store_true",
                    help="render only the campaign overview (no per-target figures)")
    args = ap.parse_args()

    summary = _load_summary()
    valid = [f for f in summary if f.get("stages")]

    if args.target:
        funnel = next((f for f in summary if f["target"] == args.target), None)
        if not funnel:
            print(f"target {args.target!r} not found in "
                  f"{DATA / 'campaign_summary.json'}")
            sys.exit(1)
        out = plot_target(funnel)
        print(f"wrote {out.relative_to(HERE)}")
        return

    # Campaign overview, then one detailed figure per target.
    out = plot_campaign(summary)
    print(f"wrote {out.relative_to(HERE)}")
    if not args.campaign_only:
        for funnel in valid:
            out = plot_target(funnel)
            print(f"wrote {out.relative_to(HERE)}")


if __name__ == "__main__":
    main()
