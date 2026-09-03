#!/usr/bin/env python3
"""Aliyun FC (bioq) only analysis and plotting.

Reads raw results from results/bioq/<svc>/N_<N>/rep_<R>/{meta.json,timing.csv,concurrency.csv},
computes statistics, and renders a multi-panel PDF figure.

Unlike analyze.py (which computes the machine-readable CSV/JSON tables), this script
does its own analysis so it works standalone against the raw results directory.

Usage:
    uv run --with matplotlib python plot_aliyun.py
    python3 plot_aliyun.py --results results/bioq --out figures/bioq.pdf
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# Use Arial for all text (matplotlib falls back per-glyph for the few symbols
# Arial lacks, e.g. the "→" arrow in panel titles), sized for a figure whose
# tight-cropped width lands below 16 cm (160 mm).
plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 8,
        "axes.titlesize": 10,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 6.5,
        "figure.titlesize": 11,
    }
)

HERE = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Brand palette (from the project README)
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

# Per-service colors (distinct for the 6 services in results/bioq)
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
SVC_MARKERS = {
    "dockq": "o",
    "plip": "s",
    "mmseqs2": "D",
    "proteinmpnn": "^",
    "rfdiffusion2": "v",
    "reinvent": "p",
    "alphafold": "h",
    "boltz": "X",
    "boltzgen": "P",
    "rfdiffusion": "*",
}

# Tier labels for legend grouping
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _mean(xs: list[float]) -> float:
    return statistics.mean(xs) if xs else 0.0


def _median(xs: list[float]) -> float:
    return statistics.median(xs) if xs else 0.0


def _stdev(xs: list[float]) -> float:
    return statistics.stdev(xs) if len(xs) > 1 else 0.0


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
def discover_services(results_root: Path) -> list[str]:
    """Discover service directories under results/bioq/ (skip non-directories)."""
    svcs = []
    if not results_root.exists():
        return svcs
    for p in sorted(results_root.iterdir()):
        if p.is_dir() and not p.name.startswith("."):
            svcs.append(p.name)
    return svcs


def discover_batch_sizes(svc_dir: Path) -> list[int]:
    """Discover N values from N_<N> directories."""
    Ns = []
    for p in sorted(svc_dir.iterdir()):
        if p.is_dir() and p.name.startswith("N_"):
            try:
                Ns.append(int(p.name.split("_", 1)[1]))
            except ValueError:
                pass
    return sorted(Ns)


def discover_replicates(n_dir: Path) -> list[int]:
    """Discover rep numbers from rep_<R> directories."""
    reps = []
    for p in sorted(n_dir.iterdir()):
        if p.is_dir() and p.name.startswith("rep_"):
            try:
                reps.append(int(p.name.split("_", 1)[1]))
            except ValueError:
                pass
    return sorted(reps)


def load_raw_results(results_root: Path) -> dict:
    """Load all raw results into a nested dict.

    Returns:
        {svc: {N: {rep: {"meta": dict, "timings": list[dict], "concurrency": list[dict]}}}}
    """
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

                # meta.json
                meta_path = rep_dir / "meta.json"
                if meta_path.exists():
                    entry["meta"] = json.loads(meta_path.read_text())

                # timing.csv
                timing_path = rep_dir / "timing.csv"
                if timing_path.exists():
                    with timing_path.open() as f:
                        entry["timings"] = list(csv.DictReader(f))

                # concurrency.csv
                conc_path = rep_dir / "concurrency.csv"
                if conc_path.exists():
                    with conc_path.open() as f:
                        entry["concurrency"] = list(csv.DictReader(f))

                results[svc][N][rep] = entry
    return results


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
def compute_per_job_latencies(results: dict) -> dict:
    """Compute per-job wall-clock latencies (t_completed - t_submit).

    Returns:
        {svc: {N: [latency_s, ...]}}  — all individual job latencies pooled across reps
    """
    latencies: dict = {}
    for svc, svc_data in results.items():
        latencies[svc] = {}
        for N, n_data in svc_data.items():
            all_lats = []
            for rep, rep_data in n_data.items():
                for t in rep_data["timings"]:
                    try:
                        t_submit = float(t["t_submit"])
                        t_completed = float(t["t_completed"])
                        lat = t_completed - t_submit
                        if lat > 0:
                            all_lats.append(lat)
                    except (ValueError, KeyError):
                        pass
            latencies[svc][N] = all_lats
    return latencies


def compute_cold_start_overhead(results: dict) -> dict:
    """Compute cold-start overhead: time from t_submit to t_running for each job.

    When ``t_running`` is unavailable (the collector's poll interval is too coarse
    to catch the ``running`` status for fast-completing jobs), falls back to the
    full per-job latency ``t_completed - t_submit`` as a conservative upper bound
    (for fast jobs the cold start dominates the total latency).

    Returns:
        {svc: {N: [overhead_s, ...]}}
    """
    overheads: dict = {}
    for svc, svc_data in results.items():
        overheads[svc] = {}
        for N, n_data in svc_data.items():
            all_ov = []
            for rep, rep_data in n_data.items():
                for t in rep_data["timings"]:
                    try:
                        t_submit = float(t["t_submit"])
                        t_completed = float(t["t_completed"])
                        t_running_str = t.get("t_running", "").strip()
                        if t_running_str:
                            t_running = float(t_running_str)
                            ov = t_running - t_submit
                        else:
                            # Fallback: treat entire job latency as overhead
                            ov = t_completed - t_submit
                        if ov >= 0:
                            all_ov.append(ov)
                    except (ValueError, KeyError):
                        pass
            overheads[svc][N] = all_ov
    return overheads


def compute_summary_table(results: dict) -> list[dict]:
    """Build a flat summary table: one row per (svc, N, rep)."""
    rows = []
    for svc, svc_data in results.items():
        # Compute single-job reference time from N=1 data
        single_times = []
        if 1 in svc_data:
            for rep_data in svc_data[1].values():
                for t in rep_data["timings"]:
                    try:
                        single_times.append(
                            float(t["t_completed"]) - float(t["t_submit"])
                        )
                    except (ValueError, KeyError):
                        pass
        single_median = _median(single_times) if single_times else 0

        for N, n_data in svc_data.items():
            for rep, rep_data in n_data.items():
                meta = rep_data["meta"]
                makespan = meta.get("makespan_s", 0)
                n_completed = meta.get("n_completed", 0)
                peak_conc = meta.get("peak_concurrency", 0)

                # Throughput: jobs/hour
                throughput = (
                    (n_completed / makespan * 3600) if makespan > 0 else 0
                )

                # Speedup vs single-job serial baseline
                serial_est = N * single_median if single_median > 0 else 0
                speedup = (serial_est / makespan) if makespan > 0 else 0

                # Per-job latencies for this rep
                rep_lats = []
                for t in rep_data["timings"]:
                    try:
                        rep_lats.append(
                            float(t["t_completed"]) - float(t["t_submit"])
                        )
                    except (ValueError, KeyError):
                        pass

                # Cold-start overheads for this rep
                # Falls back to t_completed - t_submit when t_running is missing
                rep_cold = []
                for t in rep_data["timings"]:
                    try:
                        t_submit = float(t["t_submit"])
                        t_completed = float(t["t_completed"])
                        tr = t.get("t_running", "").strip()
                        if tr:
                            ov = float(tr) - t_submit
                        else:
                            ov = t_completed - t_submit
                        if ov >= 0:
                            rep_cold.append(ov)
                    except (ValueError, KeyError):
                        pass

                rows.append(
                    {
                        "svc": svc,
                        "N": N,
                        "rep": rep,
                        "makespan_s": round(makespan, 2),
                        "throughput_jobs_per_hour": round(throughput, 1),
                        "speedup": round(speedup, 2),
                        "peak_concurrency": peak_conc,
                        "n_completed": n_completed,
                        "single_median_s": round(single_median, 2),
                        "serial_est_s": round(serial_est, 1),
                        "latency_median_s": round(_median(rep_lats), 2),
                        "latency_mean_s": round(_mean(rep_lats), 2),
                        "cold_start_median_s": round(_median(rep_cold), 2),
                        "cold_start_mean_s": round(_mean(rep_cold), 2),
                    }
                )
    return rows


def aggregate_summary(rows: list[dict]) -> dict:
    """Aggregate replicate rows into per-(svc, N) statistics.

    Returns:
        {svc: {N: {metric: value}}}
    """
    agg: dict = defaultdict(lambda: defaultdict(dict))
    # Group by (svc, N)
    groups: dict = defaultdict(list)
    for r in rows:
        groups[(r["svc"], r["N"])].append(r)

    for (svc, N), group_rows in groups.items():
        makespans = [r["makespan_s"] for r in group_rows]
        throughputs = [r["throughput_jobs_per_hour"] for r in group_rows]
        speedups = [r["speedup"] for r in group_rows]
        concs = [r["peak_concurrency"] for r in group_rows]
        cold_means = [r["cold_start_mean_s"] for r in group_rows if r["cold_start_mean_s"] > 0]
        lat_means = [r["latency_mean_s"] for r in group_rows]

        agg[svc][N] = {
            "n_replicates": len(group_rows),
            "makespan_mean_s": round(_mean(makespans), 2),
            "makespan_std_s": round(_stdev(makespans), 2),
            "makespan_values": [round(m, 2) for m in makespans],
            "throughput_mean_jph": round(_mean(throughputs), 1),
            "throughput_std_jph": round(_stdev(throughputs), 1),
            "speedup_mean": round(_mean(speedups), 2),
            "speedup_std": round(_stdev(speedups), 2),
            "peak_concurrency_mean": round(_mean(concs), 1),
            "peak_concurrency_max": max(concs) if concs else 0,
            "cold_start_mean_s": round(_mean(cold_means), 2) if cold_means else 0,
            "latency_mean_s": round(_mean(lat_means), 2),
            "latency_std_s": round(_stdev(lat_means), 2),
        }
    return agg


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
# Alpha for box-plot fills so they read as the same colour as the line plots.
BOX_ALPHA = 0.55


def _svc_label(svc: str) -> str:
    """Human-readable label with tier annotation."""
    tier = SVC_TIERS.get(svc, "")
    return f"{svc} ({tier})" if tier else svc


def _svc_color(svc: str) -> str:
    """Return the canonical colour for a service."""
    return SVC_COLORS.get(svc, TEAL)


def _svc_marker(svc: str) -> str:
    """Return the canonical marker for a service."""
    return SVC_MARKERS.get(svc, "o")


def plot_makespan(ax, agg: dict, svc_list: list[str], all_Ns: list[int]) -> None:
    """Fig (a): makespan vs N (log-log)."""
    for svc in svc_list:
        if svc not in agg:
            continue
        svc_agg = agg[svc]
        color = _svc_color(svc)
        marker = _svc_marker(svc)

        Ns = sorted(svc_agg.keys())
        means = [svc_agg[N]["makespan_mean_s"] for N in Ns]
        stds = [svc_agg[N]["makespan_std_s"] for N in Ns]

        if means:
            ax.errorbar(
                Ns, means, yerr=stds,
                fmt=f"{marker}-", color=color, capsize=4,
                label=_svc_label(svc), markersize=5, linewidth=1.4,
                markeredgewidth=1, markeredgecolor="white",
            )

    ax.set_xlabel("Number of jobs (N)", fontsize=8)
    ax.set_ylabel("Makespan (seconds)", fontsize=8)
    ax.set_title("(a) Makespan vs N", color=TEAL_DARK,
                 fontsize=10, fontweight="bold", loc="left")
    ax.set_xscale("log")
    ax.set_yscale("log")
    # (legend moved to a single shared figure legend in main())
    ax.grid(True, alpha=0.3, which="both")
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def plot_speedup(ax, agg: dict, svc_list: list[str], all_Ns: list[int]) -> None:
    """Fig (b): speedup vs N (log-log)."""
    for svc in svc_list:
        if svc not in agg:
            continue
        svc_agg = agg[svc]
        color = _svc_color(svc)
        marker = _svc_marker(svc)

        Ns = sorted(svc_agg.keys())
        speedups = [svc_agg[N]["speedup_mean"] for N in Ns]
        speedup_stds = [svc_agg[N]["speedup_std"] for N in Ns]

        if speedups:
            ax.errorbar(
                Ns, speedups, yerr=speedup_stds,
                fmt=f"{marker}-", color=color, capsize=4,
                label=_svc_label(svc), markersize=5, linewidth=1.4,
                markeredgewidth=1, markeredgecolor="white",
            )

    # Ideal speedup = N
    ax.plot(all_Ns, all_Ns, ":", color=GREY, alpha=0.5, linewidth=1.5,
            label="ideal (N×)")

    ax.set_xlabel("Number of jobs (N)", fontsize=8)
    ax.set_ylabel("Speedup vs serial", fontsize=8)
    ax.set_title("(b) Speedup vs N", color=TEAL_DARK,
                 fontsize=10, fontweight="bold", loc="left")
    ax.set_xscale("log")
    ax.set_yscale("log")
    # (legend moved to a single shared figure legend in main())
    ax.grid(True, alpha=0.3, which="both")
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def plot_throughput(ax, agg: dict, svc_list: list[str], all_Ns: list[int]) -> None:
    """Fig (c): throughput (jobs/hour) vs N."""
    for svc in svc_list:
        if svc not in agg:
            continue
        svc_agg = agg[svc]
        color = _svc_color(svc)
        marker = _svc_marker(svc)

        Ns = sorted(svc_agg.keys())
        tputs = [svc_agg[N]["throughput_mean_jph"] for N in Ns]
        tput_stds = [svc_agg[N]["throughput_std_jph"] for N in Ns]

        if tputs:
            ax.errorbar(
                Ns, tputs, yerr=tput_stds,
                fmt=f"{marker}-", color=color, capsize=4,
                label=_svc_label(svc), markersize=5, linewidth=1.4,
                markeredgewidth=1, markeredgecolor="white",
            )

    ax.set_xlabel("Number of jobs (N)", fontsize=8)
    ax.set_ylabel("Throughput (jobs / hour)", fontsize=8)
    ax.set_title("(c) Throughput vs N", color=TEAL_DARK,
                 fontsize=10, fontweight="bold", loc="left")
    # (legend moved to a single shared figure legend in main())
    ax.grid(True, alpha=0.3)
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def plot_concurrency(ax, agg: dict, svc_list: list[str], all_Ns: list[int]) -> None:
    """Fig (d): peak concurrency vs N."""
    for svc in svc_list:
        if svc not in agg:
            continue
        svc_agg = agg[svc]
        color = _svc_color(svc)
        marker = _svc_marker(svc)

        Ns = sorted(svc_agg.keys())
        conc_means = [svc_agg[N]["peak_concurrency_mean"] for N in Ns]
        conc_maxs = [svc_agg[N]["peak_concurrency_max"] for N in Ns]

        if conc_means:
            ax.plot(Ns, conc_means, f"{marker}-", color=color,
                    label=_svc_label(svc), markersize=5.5, linewidth=1.4,
                    markeredgewidth=1, markeredgecolor="white")
            # Max whisker
            ax.plot(Ns, conc_maxs, f"{marker}:", color=color,
                    markersize=3, alpha=0.4, linewidth=1)

    # Ideal: concurrency = N (every job gets its own instance)
    ax.plot(all_Ns, all_Ns, "--", color=GREY, alpha=0.5, linewidth=1.5,
            label="ideal (c=N)")

    ax.set_xlabel("Number of jobs (N)", fontsize=8)
    ax.set_ylabel("Peak concurrency", fontsize=8)
    ax.set_title("(d) Peak Concurrency vs N", color=TEAL_DARK,
                 fontsize=10, fontweight="bold", loc="left")
    # (legend moved to a single shared figure legend in main())
    ax.grid(True, alpha=0.3)
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def plot_latency_distribution(ax, latencies: dict, svc_list: list[str]) -> None:
    """Fig (e): per-job latency box plot grouped by service and N."""
    N_values = sorted(set(N for svc_lats in latencies.values() for N in svc_lats))

    # Build data for box plot: one box per (svc, N)
    positions = []
    data = []
    colors = []

    n_svcs = len(svc_list)
    width = 0.7 / n_svcs  # bar width per service

    for ni, N in enumerate(N_values):
        for si, svc in enumerate(svc_list):
            lats = latencies.get(svc, {}).get(N, [])
            if lats:
                pos = ni + 1 + (si - (n_svcs - 1) / 2) * width
                positions.append(pos)
                data.append(lats)
                colors.append(_svc_color(svc))

    if data:
        bp = ax.boxplot(
            data, positions=positions, widths=width * 0.8,
            patch_artist=True, showfliers=True,
            flierprops={"marker": ".", "markersize": 3, "alpha": 0.5},
            medianprops={"color": "black", "linewidth": 1},
            whiskerprops={"linewidth": 1},
            capprops={"linewidth": 1},
            boxprops={"linewidth": 1},
        )
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(BOX_ALPHA)

    ax.set_xticks(range(1, len(N_values) + 1))
    ax.set_xticklabels([f"N={N}" for N in N_values])
    ax.set_ylabel("Per-job latency (seconds)", fontsize=8)
    ax.set_title("(e) Per-Job Latency Distribution", color=TEAL_DARK,
                 fontsize=10, fontweight="bold", loc="left")
    ax.set_yscale("log")
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def plot_cold_start(ax, cold_start: dict, svc_list: list[str]) -> None:
    """Fig (f): cold-start overhead box plot grouped by service and N."""
    N_values = sorted(set(N for svc_ov in cold_start.values() for N in svc_ov))

    positions = []
    data = []
    colors = []

    n_svcs = len(svc_list)
    width = 0.7 / n_svcs

    for ni, N in enumerate(N_values):
        for si, svc in enumerate(svc_list):
            ovs = cold_start.get(svc, {}).get(N, [])
            if ovs:
                pos = ni + 1 + (si - (n_svcs - 1) / 2) * width
                positions.append(pos)
                data.append(ovs)
                colors.append(_svc_color(svc))

    if data:
        bp = ax.boxplot(
            data, positions=positions, widths=width * 0.8,
            patch_artist=True, showfliers=True,
            flierprops={"marker": ".", "markersize": 3, "alpha": 0.5},
            medianprops={"color": "black", "linewidth": 1},
            whiskerprops={"linewidth": 1},
            capprops={"linewidth": 1},
            boxprops={"linewidth": 1},
        )
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(BOX_ALPHA)

    ax.set_xticks(range(1, len(N_values) + 1))
    ax.set_xticklabels([f"N={N}" for N in N_values])
    ax.set_ylabel("Cold-start overhead (seconds)", fontsize=8)
    ax.set_title("(f) Cold-Start Overhead (submit → running)", color=TEAL_DARK,
                 fontsize=10, fontweight="bold", loc="left")
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def print_summary_table(rows: list[dict], agg: dict, svc_list: list[str]) -> None:
    """Print a text summary table to stdout."""
    print("\n" + "=" * 95)
    print("Bioq (Aliyun FC) Throughput Summary")
    print("=" * 95)
    print(f"{'svc':<16} {'N':<6} {'reps':<6} {'makespan(s)':<16} "
          f"{'speedup':<10} {'throughput/hr':<16} {'peak conc':<12} "
          f"{'cold start(s)':<14}")
    print("-" * 95)

    for svc in svc_list:
        if svc not in agg:
            continue
        svc_agg = agg[svc]
        for N in sorted(svc_agg.keys()):
            s = svc_agg[N]
            print(
                f"{svc:<16} {N:<6} {s['n_replicates']:<6} "
                f"{s['makespan_mean_s']:>8.1f} ±{s['makespan_std_s']:>5.1f}  "
                f"{s['speedup_mean']:>6.2f} ±{s['speedup_std']:>4.2f}  "
                f"{s['throughput_mean_jph']:>10.1f} ±{s['throughput_std_jph']:>5.1f}  "
                f"{s['peak_concurrency_mean']:>4.0f} (max {s['peak_concurrency_max']:>3.0f})  "
                f"{s['cold_start_mean_s']:>8.2f}"
            )
    print("-" * 95)
    print(f"Total rows: {len(rows)}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(
        description="bioq-only analysis and PDF plotting"
    )
    ap.add_argument(
        "--results", default=str(HERE / "results" / "bioq"),
        help="Path to results/bioq directory"
    )
    ap.add_argument(
        "--out", default=str(HERE / "figures" / "bioq.pdf"),
        help="Output PDF path"
    )
    args = ap.parse_args()

    results_root = Path(args.results)

    if not results_root.exists():
        print(f"Results directory not found: {results_root}")
        print("Run collect_bioq.py first, or use make_mock.py for mock data.")
        return

    # ---- Load ----
    print(f"Loading raw results from {results_root} ...")
    raw = load_raw_results(results_root)

    if not raw:
        print("No results found — directory exists but has no service subdirectories.")
        return

    print(f"Found {len(raw)} services: {', '.join(sorted(raw.keys()))}")

    # ---- Analyze ----
    print("Computing statistics ...")
    rows = compute_summary_table(raw)
    agg = aggregate_summary(rows)
    latencies = compute_per_job_latencies(raw)
    cold_start = compute_cold_start_overhead(raw)

    # Collect all N values across all services
    all_Ns = sorted(set(N for svc_data in raw.values() for N in svc_data))
    # Canonical service list — same order for every subplot (alphabetical)
    svc_list = sorted(raw.keys())

    # Print text summary
    print_summary_table(rows, agg, svc_list)

    # ---- Plot ----
    print(f"\nRendering figures to {args.out} ...")

    # 3×2 grid whose tight-cropped PDF width lands below 16 cm (160 mm).
    fig = plt.figure(figsize=(6.25, 6.0), facecolor="white")

    # 3×2 grid
    gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.30)

    ax_makespan = fig.add_subplot(gs[0, 0])
    ax_speedup = fig.add_subplot(gs[0, 1])
    ax_throughput = fig.add_subplot(gs[1, 0])
    ax_concurrency = fig.add_subplot(gs[1, 1])
    ax_latency = fig.add_subplot(gs[2, 0])
    ax_cold = fig.add_subplot(gs[2, 1])

    plot_makespan(ax_makespan, agg, svc_list, all_Ns)
    plot_speedup(ax_speedup, agg, svc_list, all_Ns)
    plot_throughput(ax_throughput, agg, svc_list, all_Ns)
    plot_concurrency(ax_concurrency, agg, svc_list, all_Ns)
    plot_latency_distribution(ax_latency, latencies, svc_list)
    plot_cold_start(ax_cold, cold_start, svc_list)

    # Shared legend — all six panels are colour-coded by service, so a single
    # bottom legend replaces the per-panel legends (which would overflow the
    # 16 cm width at this scale).
    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D(
            [0], [0], color=_svc_color(svc), marker=_svc_marker(svc),
            linestyle="-", linewidth=1.4, markersize=5,
            markeredgecolor="white", markeredgewidth=1,
            label=_svc_label(svc),
        )
        for svc in svc_list
    ]
    fig.legend(
        handles=legend_handles, loc="upper center", bbox_to_anchor=(0.5, -0.03),
        ncol=3, frameon=False, fontsize=6.5, handlelength=1.6,
        columnspacing=1.0, handletextpad=0.4,
    )

    # Suptitle
    fig.suptitle(
        "Bioq Throughput Scaling on Aliyun Function Compute",
        color=TEAL_DARK, fontsize=11, fontweight="bold", y=1.01
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
