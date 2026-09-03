#!/usr/bin/env python3
"""Plot cost vs duty-cycle curve (the cost model figure).

Reads break_even.json (and sensitivity.json when present) from the model and
produces:

  figures/E4_cost_curve.pdf     — cost vs duty-cycle with break-even mark

The $/job-per-service table is delivered as ``data/cost_table.csv`` (no PDF —
see README.md).

Usage:
    python3 plot.py
    python3 plot.py --data-dir path/to/data --out-dir path/to/figures

Requires: matplotlib, numpy (``uv run --with matplotlib,numpy``).

Styled to match the throughput-scaling figures; see ``docs/plotting-style-guide.md``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import config  # noqa: E402

# ---------------------------------------------------------------------------
# Brand palette (from the repo style guide; matches the throughput-scaling plot scripts).
# See docs/plotting-style-guide.md.
# ---------------------------------------------------------------------------
TEAL_DARK = "#05668D"
TEAL = "#028090"
GREEN = "#02C39A"
AMBER = "#F0A202"
BG = "#E8F6F3"
RED = "#C1361D"
GREY = "#9AA7AD"


def _lighten(hex_color: str, factor: float) -> str:
    """Blend a hex colour toward white by *factor* (0 = original, 1 = white)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def _style_axes(ax, title: str) -> None:
    """Apply the signature panel grammar (docs/plotting-style-guide.md §3)."""
    ax.set_facecolor(BG)
    ax.grid(True, alpha=0.3)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GREY)
    ax.set_title(title, color=TEAL_DARK, fontsize=13,
                 fontweight="bold", loc="left")


def _load_data(data_dir: Path) -> tuple[list[dict], dict]:
    be_path = data_dir / "break_even.json"
    sens_path = data_dir / "sensitivity.json"
    if not be_path.is_file():
        raise SystemExit(f"break_even.json not found: {be_path}")
    with open(be_path) as f:
        be_data = json.load(f)
    sens_data = {}
    if sens_path.is_file():
        with open(sens_path) as f:
            sens_data = json.load(f)
    return be_data, sens_data


def plot_cost_curve(be_data: list[dict], sens_data: dict,
                    out: Path, figsize: tuple[int, int]) -> None:
    """Cost model figure: cost vs duty-cycle break-even curve.

    One panel showing the flat dedicated line crossed by the linear serverless
    line, with a sensitivity band and the break-even d* marked.
    """
    # Pick the "all on A100" entry (last in be_data, or explicitly the weighted mix)
    be = None
    for b in be_data:
        if b.get("gpu_class") == "A100" and "duty_cycle_pct" in str(b.get("break_even_duty_cycle_pct", "")):
            pass
    # Use the last entry (all-services on A100 with weighted mix)
    be = be_data[-1] if be_data else be_data[0]

    if be is None:
        print("  no break-even data to plot")
        return

    dedicated_monthly = be["dedicated_monthly_usd"]
    wavg_job_cost = be["wavg_job_cost_usd"]
    max_jobs = be["max_jobs_per_month_at_d1"]
    d_star = be["break_even_duty_cycle"]
    d_star_pct = be["break_even_duty_cycle_pct"]

    # Duty cycle sweep
    d = np.linspace(0, 1, 200)
    serverless = d * max_jobs * wavg_job_cost
    dedicated = np.full_like(d, dedicated_monthly)

    # Sensitivity band: price ±30 %
    def _serverless_for_price_mult(m: float) -> np.ndarray:
        return d * max_jobs * wavg_job_cost * m

    price_pcts = config.GPU_PRICE_SENSITIVITY_PCT
    # Find the min and max across all price scenarios
    sens_lower = _serverless_for_price_mult(1 + min(price_pcts) / 100)
    sens_upper = _serverless_for_price_mult(1 + max(price_pcts) / 100)

    fig, ax = plt.subplots(figsize=figsize, facecolor="white")

    # Sensitivity band: serverless price ±X%, drawn in the main hue.
    ax.fill_between(d, sens_lower, sens_upper, alpha=0.15, color=TEAL,
                    label=f"FC price sensitivity\n"
                          f"({min(price_pcts):+d}% to {max(price_pcts):+d}%)")

    # Main lines: serverless (the main story) vs dedicated (neutral baseline).
    ax.plot(d, dedicated, color=GREY, linewidth=2.5,
            label="Dedicated GPU (amortized)")
    ax.plot(d, serverless, color=TEAL, linewidth=2.5, label="Serverless (FC)")

    # Break-even point (key data → amber; dashed grey guides).
    ax.axvline(x=d_star, color=GREY, linewidth=1, linestyle="--", alpha=0.7)
    ax.axhline(y=dedicated_monthly, color=GREY, linewidth=1, linestyle="--",
               alpha=0.3)
    be_cost = d_star * max_jobs * wavg_job_cost
    ax.plot(d_star, be_cost, "o", color=AMBER, markersize=8,
            markeredgecolor="white", markeredgewidth=1.5, zorder=5)
    ax.annotate(
        f"  d* = {d_star_pct:.1f}%\n  ${be_cost:.0f}/mo",
        xy=(d_star, be_cost),
        xytext=(min(d_star + 0.08, 0.85), be_cost * 1.3),
        fontsize=8,
        ha="left",
        color=TEAL_DARK,
        arrowprops=dict(arrowstyle="->", color=TEAL_DARK, lw=0.8),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                  edgecolor=GREY, alpha=0.9),
    )

    # Axes + signature panel grammar.
    ax.set_xlabel("Duty cycle (fraction of wall-clock GPU is busy)", fontsize=11)
    ax.set_ylabel("Monthly cost (USD)", fontsize=11)
    _style_axes(ax, "Monthly cost vs duty cycle")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, max(dedicated.max(), serverless.max()) * 1.25)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x * 100:.0f}%"))
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("$%.0f"))
    ax.legend(loc="upper left", fontsize=8, frameon=False)

    # Annotation box with key assumptions.
    assumptions = (
        f"GPU: {be['gpu_class']}  |  "
        f"FC: ${be['fc_rate_usd_per_sec']:.6f}/s "
        f"(CU-billed, {be['cu_per_gpu_sec']:.0f} CU/s, "
        f"¥{be['fc_rate_cny_per_sec']:.6f}/s)  |  "
        f"Dedicated: ${be['dedicated_purchase_usd']:.0f} "
        f"over {be['dedicated_lifetime_years']:.0f} yr\n"
        f"Rate card: {config.FC_RATE_CARD_DATE.isoformat()} "
        f"(CU model, ¥{config.CU_TIER_PRICING[config.CU_DEFAULT_TIER][1]:.5f}/CU, "
        f"${1/config.CNY_PER_USD:.3f}/¥)  |  "
        f"Cold-start: {config.COLD_START_OVERHEAD_SEC}s  |  "
        f"Max jobs/mo @ 100%: {be['max_jobs_per_month_at_d1']:.0f}"
    )
    ax.text(0.98, 0.02, assumptions, transform=ax.transAxes, ha="right",
            va="bottom", fontsize=6.5, color=GREY,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                      edgecolor=GREY, alpha=0.85))

    fig.suptitle("Serverless vs Dedicated GPU: Monthly Cost Break-Even",
                 color=TEAL_DARK, fontsize=15, fontweight="bold", y=1.03)
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight", pad_inches=0.15,
                facecolor="white")
    plt.close(fig)
    print(f"  cost curve           -> {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=HERE / "data",
                    help="model output data directory")
    ap.add_argument("--out-dir", type=Path, default=HERE / "figures",
                    help="output figure directory")
    ap.add_argument("--figsize", nargs=2, type=float, default=(8, 5.5),
                    help="figure size in inches (default: 8 5.5)")
    args = ap.parse_args()

    data_dir = args.data_dir.expanduser().resolve()
    out_dir = args.out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    be_data, sens_data = _load_data(data_dir)

    print("generating figures ...")
    plot_cost_curve(be_data, sens_data, out_dir / "E4_cost_curve.pdf",
                    tuple(args.figsize))

    print(f"\ndone -> {out_dir}")


if __name__ == "__main__":
    main()