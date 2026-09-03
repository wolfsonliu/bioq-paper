#!/usr/bin/env python3
"""bioq-only box plots grouped by **service** (not by N).

Reads raw results from results/bioq/<svc>/N_<N>/rep_<R>/{timing.csv,…},
computes per-job latency and cold-start overhead, and renders a 2‑panel
PDF where each panel groups boxes by service, with three boxes per service
(N=1, N=10, N=50).

Usage:
    python3 plot_aliyun_by_service.py
    python3 plot_aliyun_by_service.py --results results/bioq --out figures/bioq_by_service.pdf
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Use Arial for all text (per-glyph fallback for glyphs Arial lacks, e.g. "→").
plt.rcParams.update({"font.family": "Arial"})

try:
    from scipy import stats as _sp
except ImportError:
    _sp = None

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Brand palette
# ---------------------------------------------------------------------------
TEAL_DARK = "#05668D"
TEAL = "#028090"
GREEN = "#02C39A"
AMBER = "#F0A202"
BG = "#E8F6F3"
RED = "#C1361D"
GREY = "#9AA7AD"
PURPLE = "#7B2D8E"
BLUE = "#2E86AB"
ORANGE = "#E76F51"

SVC_COLORS = {
    "dockq": TEAL,
    "plip": GREEN,
    "mmseqs2": AMBER,
    "proteinmpnn": BLUE,
    "rfdiffusion2": RED,
    "reinvent": PURPLE,
    "alphafold": ORANGE,
    "boltz": GREY,
    "boltzgen": "#5C4B51",
    "rfdiffusion": "#8CB369",
}

SVC_TIERS = {
    "dockq": "cold (CPU)",
    "plip": "cold (CPU)",
    "mmseqs2": "hot (GPU)",
    "proteinmpnn": "hot (GPU)",
    "rfdiffusion2": "warm (GPU)",
    "reinvent": "warm (GPU)",
    "alphafold": "warm (GPU)",
    "boltz": "warm (GPU)",
    "boltzgen": "warm (GPU)",
    "rfdiffusion": "warm (GPU)",
}

# Alpha values for N=1, N=10, N=50 — lighter → darker
N_ALPHAS = {1: 0.30, 10: 0.55, 50: 0.80}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _mean(xs: list[float]) -> float:
    return statistics.mean(xs) if xs else 0.0


def _median(xs: list[float]) -> float:
    return statistics.median(xs) if xs else 0.0


# ---------------------------------------------------------------------------
# Data loading (reuses the same logic as plot_aliyun.py)
# ---------------------------------------------------------------------------
def discover_services(results_root: Path) -> list[str]:
    svcs = []
    if not results_root.exists():
        return svcs
    for p in sorted(results_root.iterdir()):
        if p.is_dir() and not p.name.startswith("."):
            svcs.append(p.name)
    return svcs


def discover_batch_sizes(svc_dir: Path) -> list[int]:
    Ns = []
    for p in sorted(svc_dir.iterdir()):
        if p.is_dir() and p.name.startswith("N_"):
            try:
                Ns.append(int(p.name.split("_", 1)[1]))
            except ValueError:
                pass
    return sorted(Ns)


def discover_replicates(n_dir: Path) -> list[int]:
    reps = []
    for p in sorted(n_dir.iterdir()):
        if p.is_dir() and p.name.startswith("rep_"):
            try:
                reps.append(int(p.name.split("_", 1)[1]))
            except ValueError:
                pass
    return sorted(reps)


def load_raw_results(results_root: Path) -> dict:
    results: dict = {}
    for svc in discover_services(results_root):
        svc_dir = results_root / svc
        results[svc] = {}
        for N in discover_batch_sizes(svc_dir):
            n_dir = svc_dir / f"N_{N}"
            results[svc][N] = {}
            for rep in discover_replicates(n_dir):
                rep_dir = n_dir / f"rep_{rep}"
                entry: dict = {"meta": {}, "timings": [], "concurrency": []}
                meta_path = rep_dir / "meta.json"
                if meta_path.exists():
                    entry["meta"] = json.loads(meta_path.read_text())
                timing_path = rep_dir / "timing.csv"
                if timing_path.exists():
                    with timing_path.open() as f:
                        entry["timings"] = list(csv.DictReader(f))
                conc_path = rep_dir / "concurrency.csv"
                if conc_path.exists():
                    with conc_path.open() as f:
                        entry["concurrency"] = list(csv.DictReader(f))
                results[svc][N][rep] = entry
    return results


def compute_per_job_latencies(results: dict) -> dict:
    """{svc: {N: [latency_s, ...]}}"""
    latencies: dict = {}
    for svc, svc_data in results.items():
        latencies[svc] = {}
        for N, n_data in svc_data.items():
            all_lats = []
            for rep_data in n_data.values():
                for t in rep_data["timings"]:
                    try:
                        lat = float(t["t_completed"]) - float(t["t_submit"])
                        if lat > 0:
                            all_lats.append(lat)
                    except (ValueError, KeyError):
                        pass
            latencies[svc][N] = all_lats
    return latencies


def compute_cold_start_overhead(results: dict) -> dict:
    """{svc: {N: [overhead_s, ...]}}

    When ``t_running`` is unavailable (the collector's poll interval is too coarse
    to catch the ``running`` status for fast-completing jobs), falls back to the
    full per-job latency ``t_completed - t_submit`` as a conservative upper bound
    (for fast jobs the cold start dominates the total latency).
    """
    overheads: dict = {}
    for svc, svc_data in results.items():
        overheads[svc] = {}
        for N, n_data in svc_data.items():
            all_ov = []
            for rep_data in n_data.values():
                for t in rep_data["timings"]:
                    try:
                        t_submit = float(t["t_submit"])
                        t_completed = float(t["t_completed"])
                        tr = t.get("t_running", "").strip()
                        if tr:
                            ov = float(tr) - t_submit
                        else:
                            # Fallback: treat entire job latency as overhead
                            ov = t_completed - t_submit
                        if ov >= 0:
                            all_ov.append(ov)
                    except (ValueError, KeyError):
                        pass
            overheads[svc][N] = all_ov
    return overheads


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def _svc_label(svc: str) -> str:
    tier = SVC_TIERS.get(svc, "")
    return f"{svc}\n({tier})" if tier else svc


def _lighten(hex_color: str, factor: float) -> str:
    """Blend a hex colour toward white by *factor* (0 = original, 1 = white)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def _stars(p) -> str:
    """Significance stars from a two-sided p-value."""
    if p is None:
        return ""
    if p < 1e-4:
        return "****"
    if p < 1e-3:
        return "***"
    if p < 1e-2:
        return "**"
    if p < 0.05:
        return "*"
    return "ns"


def _mannwhitney_p(a, b) -> float | None:
    """Two-sided exact Mann-Whitney U p between two per-job samples."""
    if _sp is None:
        return None
    a = [float(x) for x in a]
    b = [float(x) for x in b]
    if len(a) < 2 or len(b) < 2:
        return None
    try:
        return float(_sp.mannwhitneyu(a, b, alternative="two-sided",
                                      method="exact").pvalue)
    except (ValueError, MemoryError):
        return None


def _whisker_hi(vals) -> float:
    """Top of a box whisker (excludes fliers), used to place brackets."""
    vals = sorted(float(v) for v in vals)
    q1 = float(np.percentile(vals, 25))
    q3 = float(np.percentile(vals, 75))
    iqr = q3 - q1
    return min(vals[-1], q3 + 1.5 * iqr)


def _draw_service_grouped_boxes(
    ax,
    data_dict: dict,          # {svc: {N: [values]}}
    svc_list: list[str],
    N_values: list[int],
    ylabel: str,
    title: str,
    y_log: bool = False,
    sig: bool = False,
) -> None:
    """Draw grouped box plots: x-axis = services, within each group = N values.

    Each service gets its canonical colour; N=1/10/50 are distinguished by
    alpha (lighter → darker) so the same hue family is preserved.

    When ``sig`` is True, a significance bracket is drawn between each adjacent
    pair of N levels above each service, starred (or ``ns``) from the two-sided
    exact Mann-Whitney U p-value on the per-job values pooled across replicates.
    """
    n_svcs = len(svc_list)
    n_Ns = len(N_values)

    # Group width per service, box width per N
    group_width = 0.75
    box_width = group_width / n_Ns * 0.85

    for si, svc in enumerate(svc_list):
        svc_color = SVC_COLORS.get(svc, TEAL)
        x_center = si + 1  # 1-based for tick labels

        for ni, N in enumerate(N_values):
            vals = data_dict.get(svc, {}).get(N, [])
            if not vals:
                continue

            # Position within the group
            offset = (ni - (n_Ns - 1) / 2) * box_width
            pos = x_center + offset

            alpha = N_ALPHAS.get(N, 0.55)
            bp = ax.boxplot(
                [vals],
                positions=[pos],
                widths=box_width * 0.9,
                patch_artist=True,
                showfliers=True,
                flierprops={"marker": ".", "markersize": 2.5, "alpha": 0.4},
                medianprops={"color": "black", "linewidth": 1.0},
                whiskerprops={"linewidth": 0.7},
                capprops={"linewidth": 0.7},
                boxprops={"linewidth": 0.7},
            )
            for patch in bp["boxes"]:
                patch.set_facecolor(svc_color)
                patch.set_alpha(alpha)

    # X-axis: service names
    ax.set_xticks(range(1, n_svcs + 1))
    ax.set_xticklabels([_svc_label(svc) for svc in svc_list], fontsize=6.5)

    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, color=TEAL_DARK, fontsize=10.5, fontweight="bold", loc="left")

    if y_log:
        ax.set_yscale("log")

    ax.grid(True, alpha=0.3, axis="y")
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # Legend: N values with alpha
    from matplotlib.patches import Patch
    legend_patches = [
        Patch(facecolor=GREY, alpha=N_ALPHAS.get(N, 0.55),
              label=f"N={N}", edgecolor="black", linewidth=0.5)
        for N in N_values
    ]
    ax.legend(handles=legend_patches, fontsize=7, frameon=False,
              ncol=len(N_values), loc="upper right",
              title="Batch size", title_fontsize=7)

    # Significance brackets between adjacent N levels (Mann-Whitney, job level).
    if sig and _sp is not None:
        # Bracket geometry is computed in the axis's native space — the raw
        # value on a linear axis, or log10(value) on a log axis — so the gap
        # between an anchor and its bracket (and between stacked brackets for
        # successive N pairs) stays a constant visual offset regardless of the
        # data's magnitude, and the round-trip back to data coordinates keeps
        # the brackets correctly positioned on a log-scaled axis.
        def _to_axis(v: float) -> float:
            return float(np.log10(v)) if y_log else float(v)

        def _from_axis(p: float) -> float:
            return float(10 ** p) if y_log else float(p)

        all_vals = [v for s in svc_list for N in N_values
                    for v in data_dict.get(s, {}).get(N, [])]
        gmin = _to_axis(min(all_vals)) if all_vals else 0.0
        gmax = _to_axis(max(all_vals)) if all_vals else 1.0
        step = (gmax - gmin) * 0.03 if gmax > gmin else 0.05
        max_top = gmax
        for si, svc in enumerate(svc_list):
            x_center = si + 1
            wh = {}
            for N in N_values:
                v = data_dict.get(svc, {}).get(N, [])
                if len(v) >= 2:
                    wh[N] = _to_axis(_whisker_hi(v))
            y_top_prev = None
            for i in range(len(N_values) - 1):
                na, nb = N_values[i], N_values[i + 1]
                va = data_dict.get(svc, {}).get(na, [])
                vb = data_dict.get(svc, {}).get(nb, [])
                p = _mannwhitney_p(va, vb)
                if p is None:
                    continue
                anchor = max(wh[na], wh[nb])
                y_top = anchor + step
                if y_top_prev is not None:
                    y_top = max(y_top, y_top_prev + 2 * step)
                xa = x_center + (i - (n_Ns - 1) / 2) * box_width
                xb = x_center + ((i + 1) - (n_Ns - 1) / 2) * box_width
                ax.plot([xa, xa, xb, xb],
                        [_from_axis(anchor), _from_axis(y_top),
                         _from_axis(y_top), _from_axis(anchor)],
                        color="0.2", lw=0.9, clip_on=False)
                ax.text((xa + xb) / 2, _from_axis(y_top), _stars(p),
                        ha="center", va="bottom", fontsize=6.5, color="0.2")
                y_top_prev = y_top
                max_top = max(max_top, y_top)
        lo, hi = ax.get_ylim()
        lo_a, hi_a = _to_axis(lo), _to_axis(hi)
        ax.set_ylim(_from_axis(lo_a), max(_from_axis(hi_a), _from_axis(max_top + 4 * step)))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(
        description="bioq box plots grouped by service"
    )
    ap.add_argument(
        "--results", default=str(HERE / "results" / "bioq"),
        help="Path to results/bioq directory"
    )
    ap.add_argument(
        "--out", default=str(HERE / "figures" / "bioq_by_service.pdf"),
        help="Output PDF path"
    )
    args = ap.parse_args()

    results_root = Path(args.results)
    if not results_root.exists():
        print(f"Results directory not found: {results_root}")
        return

    print(f"Loading raw results from {results_root} ...")
    raw = load_raw_results(results_root)
    if not raw:
        print("No results found.")
        return

    svc_list = sorted(raw.keys())
    # Collect all N values across all services
    N_values = sorted(set(N for svc_data in raw.values() for N in svc_data))
    print(f"Services: {', '.join(svc_list)}")
    print(f"Batch sizes: {N_values}")

    print("Computing statistics ...")
    latencies = compute_per_job_latencies(raw)
    cold_start = compute_cold_start_overhead(raw)

    # ---- Plot ----
    print(f"Rendering to {args.out} ...")

    # Publication column limit: final width ≤ 16 cm. The canvas is set to that
    # width; the only element wide enough to overflow it is the one-line
    # suptitle, whose font size is kept small enough to stay within 16 cm.
    fig_w_in = 16.0 / 2.54
    fig, (ax_lat, ax_cold) = plt.subplots(
        2, 1, figsize=(fig_w_in, 6.4), facecolor="white",
        gridspec_kw={"hspace": 0.32},
    )

    _draw_service_grouped_boxes(
        ax_lat, latencies, svc_list, N_values,
        ylabel="Per-job latency (seconds)",
        title="(a) Per-Job Latency Distribution — grouped by service",
        y_log=True,
        sig=True,
    )

    _draw_service_grouped_boxes(
        ax_cold, cold_start, svc_list, N_values,
        ylabel="Cold-start overhead (seconds)",
        title="(b) Cold-Start Overhead (submit → running) — grouped by service",
        y_log=False,
        sig=True,
    )

    fig.suptitle(
        "Bioq Latency & Cold-Start Analysis on Aliyun Function Compute",
        color=TEAL_DARK, fontsize=11, fontweight="bold", y=1.01,
    )

    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, bbox_inches="tight", format="pdf")
    try:
        print(f"Wrote {out.relative_to(HERE)}")
    except ValueError:
        print(f"Wrote {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
