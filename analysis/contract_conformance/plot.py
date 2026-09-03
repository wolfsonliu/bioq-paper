#!/usr/bin/env python3
"""Contract-conformance figure: endpoint-surface bars + checklist/doc-depth heatmap.

Reads score.py outputs (data/scores.csv, data/conformance.csv,
data/summary.json) and renders one vertical, narrow two-panel figure. Services
run LEFT → RIGHT (one column per service) so the whole figure stays within
16 cm wide:

  top     per-service endpoint surface — a vertical bar whose dark base segment
          is the number of `bioq run` task endpoints and whose light top segment
          is the remaining (legacy) endpoints. The task segment is teal when the
          service sits at/above the conformance bar and amber when below it.
  bottom  checklist x service heatmap — 6 rows: the five scored checklist pass
          rates plus `field_desc_frac` (mean fraction of request fields carrying
          a description), a non-scored "documentation depth" gradient rendered in
          a warm ramp and separated from the scored rows by a divider line.

The two panels share their x-axis, so every service column lines up one-to-one;
service names are printed once, rotated 90°, under the heatmap.

Outputs:
  figures/fig-conformance.pdf / .png

Usage:
    python3 plot.py
    python3 plot.py --threshold 0.9 --dpi 150

Requires: matplotlib (``uv run --with matplotlib``).
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless — no DISPLAY needed
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch, Rectangle

# Brand palette (house figure colors)
TEAL_DARK = "#05668D"
TEAL = "#028090"
GREEN = "#02C39A"
AMBER = "#F0A202"
BG = "#E8F6F3"
GREY = "#9AA7AD"


def _lighten(hex_color: str, factor: float) -> str:
    """Blend a brand hex toward white."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


LEGACY = _lighten(GREY, 0.4)  # non-task endpoints: muted/inactive tint of GREY

CHECKS = ["typed_params", "file_fields", "defaults", "machine_view", "docs_text"]
CHECK_LABELS = ["typed\nparams", "file\nfields", "defaults", "machine\nview", "docs\ntext"]


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--threshold", type=float, default=0.9)
    ap.add_argument("--data-dir", default=str(Path(__file__).parent / "data"))
    ap.add_argument("--out-dir", default=str(Path(__file__).parent / "figures"))
    ap.add_argument("--dpi", type=int, default=150)
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scores = load_rows(data_dir / "scores.csv")
    conf = load_rows(data_dir / "conformance.csv")
    summary = json.loads((data_dir / "summary.json").read_text(encoding="utf-8"))

    # Audited services only, sorted by endpoint surface (desc) for a monotonic
    # left-to-right size gradient.
    unaudited = [r["service"] for r in scores if r.get("status") == "unaudited"]
    scores = [r for r in scores if r.get("status") != "unaudited"]
    scores.sort(key=lambda r: (-int(r["n_endpoints"]),
                               -int(r["n_task_endpoints"]),
                               r["service"]))
    svcs = [r["service"] for r in scores]
    n = len(svcs)
    xs = list(range(n))

    # per-service × per-check pass rate and field-description coverage over task
    # endpoints (fallback: all).
    checks_pass: dict[str, list[float]] = {}
    field_desc: dict[str, float] = {}
    for r in scores:
        svc = r["service"]
        rows = [x for x in conf if x["service"] == svc and x["is_task"] == "1"] \
            or [x for x in conf if x["service"] == svc]
        checks_pass[svc] = [
            sum(x[c] == "1" for x in rows) / len(rows) if rows else 0.0
            for c in CHECKS
        ]
        field_desc[svc] = (
            sum(float(x["field_desc_frac"]) for x in rows) / len(rows)
            if rows else 0.0
        )

    cmap_checks = LinearSegmentedColormap.from_list("checks", [BG, GREEN, TEAL])
    cmap_desc = LinearSegmentedColormap.from_list("desc",
                                                  [_lighten(AMBER, 0.9), AMBER])

    # 6.0 in ≈ 15.2 cm — under the 16 cm-wide budget even after label margins.
    # The heatmap is drawn with aspect="equal" so its cells are perfect squares
    # (30 columns => the 6 rows render as a wide, short strip).
    fig = plt.figure(figsize=(6.0, 4.4), layout="constrained")
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(2, 1, height_ratios=[1.5, 1.0], hspace=0.02)
    ax_bar = fig.add_subplot(gs[0])
    ax_heat = fig.add_subplot(gs[1], sharex=ax_bar)
    ax_heat.set_aspect("equal")
    for ax in (ax_bar, ax_heat):
        ax.set_facecolor(BG)

    # ---- top: endpoint-surface bars (task base + legacy top) -----------------
    task_vals = [int(r["n_task_endpoints"]) for r in scores]
    tot_vals = [int(r["n_endpoints"]) for r in scores]
    legacy_vals = [t - k for t, k in zip(tot_vals, task_vals)]
    task_colors = [TEAL if float(r["score_task"]) >= args.threshold else AMBER
                   for r in scores]

    ax_bar.bar(xs, task_vals, bottom=0, width=0.72, color=task_colors,
               edgecolor="white", linewidth=0.5, zorder=2)
    ax_bar.bar(xs, legacy_vals, bottom=task_vals, width=0.72, color=LEGACY,
               edgecolor="white", linewidth=0.5, zorder=1)
    ax_bar.set_axisbelow(True)
    ax_bar.grid(True, alpha=0.3, axis="y", zorder=0)
    for x, tot in zip(xs, tot_vals):
        ax_bar.text(x, tot + 0.15, str(tot), ha="center", va="bottom",
                    fontsize=5, color=GREY)

    xmax = max(tot_vals)
    ax_bar.set_xlim(-0.5, n - 0.5)
    ax_bar.set_ylim(0, xmax * 1.18)
    ax_bar.set_yticks(range(0, xmax + 1, 2))
    ax_bar.tick_params(axis="y", labelsize=7)
    ax_bar.set_ylabel("endpoints", fontsize=8.5, color=TEAL_DARK)
    ax_bar.set_title("(a) Endpoint surface", fontsize=9.5, color=TEAL_DARK,
                     loc="left", weight="bold")
    ax_bar.text(0.995, 0.985,
                "* field_desc = fraction of request fields carrying a "
                "description\n(non-scored)",
                transform=ax_bar.transAxes, ha="right", va="top",
                fontsize=5.3, color=GREY, linespacing=1.3)
    ax_bar.tick_params(axis="x", labelbottom=False)  # names live under the heatmap
    for s in ("top", "right"):
        ax_bar.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax_bar.spines[s].set_color(GREY)

    # ---- bottom: checklist × service heatmap ---------------------------------
    # row 0 (typed_params) at top → y = 5; field_desc at bottom → y = 0
    ax_heat.set_xlim(-0.5, n - 0.5)
    ax_heat.set_ylim(-0.5, 5.5)
    for j, svc in enumerate(svcs):
        for c in range(len(CHECKS)):
            v = checks_pass[svc][c]
            y = 5 - c
            ax_heat.add_patch(Rectangle(
                (j - 0.5, y - 0.5), 1, 1,
                facecolor=cmap_checks(v), edgecolor="white", linewidth=0.4))
            if v < 1.0:  # flag the failing cell (the straggler)
                ax_heat.text(j, y, "0", ha="center", va="center",
                             fontsize=4.5, color=TEAL_DARK, weight="bold")
        v = field_desc[svc]
        ax_heat.add_patch(Rectangle(
            (j - 0.5, -0.5), 1, 1,
            facecolor=cmap_desc(v), edgecolor="white", linewidth=0.4))
        ax_heat.text(j, 0, f"{v:.2f}", ha="center", va="center",
                     fontsize=4.3, color="white" if v > 0.6 else TEAL_DARK)

    ax_heat.axhline(0.5, color=GREY, lw=1.2)  # scored | non-scored divider
    ax_heat.set_yticks([5, 4, 3, 2, 1, 0])
    ax_heat.set_yticklabels(CHECK_LABELS + ["field\ndesc*"],
                            fontsize=5.2, color=TEAL_DARK)
    ax_heat.set_xticks(xs)
    ax_heat.set_xticklabels(svcs, rotation=90, fontsize=5.3, color=TEAL_DARK)
    ax_heat.set_title("(b) Conformance checklist × documentation depth",
                      fontsize=9.5, color=TEAL_DARK, loc="left", weight="bold")
    for s in ("left", "bottom"):
        ax_heat.spines[s].set_color(GREY)
    for s in ("top", "right"):
        ax_heat.spines[s].set_visible(False)

    # ---- legend + headline + footnotes ---------------------------------------
    handles = [
        Patch(color=TEAL, label="task endpoints · conformant (≥ 0.9)"),
        Patch(color=AMBER, label="task endpoints · below 0.9"),
        Patch(color=LEGACY, label="non-task endpoints"),
    ]
    fig.legend(handles=handles, loc="outside lower center", ncol=3,
               fontsize=7, frameon=False)
    fig.suptitle(
        f"{summary['pct_endpoints_fully_conformant_task']:.0f}% of task endpoints "
        f"fully conformant · {summary['pct_services_above_threshold']:.0f}% of "
        f"services ≥ {args.threshold:.0%} · median service score "
        f"{summary['median_service_score_task']:.2f}",
        fontsize=9, color=TEAL_DARK)
    if unaudited:
        fig.text(0.99, 0.012,
                 f"not shown (no manifest at audit time, excluded): "
                 f"{', '.join(unaudited)}",
                 fontsize=5.8, color=GREY, ha="right")

    pdf = out_dir / "fig-conformance.pdf"
    png = out_dir / "fig-conformance.png"
    fig.savefig(pdf, bbox_inches="tight")
    fig.savefig(png, dpi=args.dpi, bbox_inches="tight")
    here = Path(__file__).resolve().parent
    for p in (pdf, png):
        try:
            print(f"wrote {p.relative_to(here)}")
        except ValueError:
            print(f"wrote {p}")


if __name__ == "__main__":
    main()
