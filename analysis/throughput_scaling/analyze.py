#!/usr/bin/env python3
"""Offline analysis: process Aliyun FC (bioq) timing logs into
throughput / makespan / speedup-vs-serial tables, plus statistical tests.

Reads collected results from:
    results/bioq/<svc>/N_<N>/rep_<R>/meta.json + timing.csv

Outputs:
    data/throughput.csv          — per-(svc, N, rep) throughput + makespan + speedup
    data/scaling_summary.json    — aggregated stats per (svc, N)
    data/single_job_stats.json   — per-service single-job timing stats (serial baseline)
    data/statistical_tests.json  — omnibus + pairwise tests of each metric across N
    data/statistical_tests.csv   — flat version of the above

Usage:
    python3 analyze.py
    python3 analyze.py --bioq results/bioq

The statistical pass needs scipy; without it the tables above still generate and
the tests are skipped with a warning.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path

from config import SERVICES, BATCH_SIZES, REPLICATES

try:
    from scipy import stats as _sp
except ImportError:  # pragma: no cover — scipy is optional for the stats pass
    _sp = None

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

# Significance threshold for flagging tests.
ALPHA = 0.05

# Metrics compared across batch sizes N at the *replicate* level (n = replicates
# per N, i.e. 3). These match the columns of data/throughput.csv.
REPLICATE_METRICS = [
    "makespan_s",
    "throughput_jobs_per_hour",
    "speedup_vs_serial",
    "peak_concurrency",
    "cold_start_s",
]

# Metrics compared across N at the *job* level (n = jobs pooled across the
# replicates of each N, i.e. 3 × N). Richer for per-job quantities like cold
# start, where the replicate-level median discards most of the signal.
JOB_METRICS = ["cold_start_s", "latency_s"]


def _read_meta(p: Path) -> dict:
    m = p / "meta.json"
    return json.loads(m.read_text()) if m.exists() else {}


def _read_timing(p: Path) -> list[dict]:
    t = p / "timing.csv"
    if not t.exists():
        return []
    with t.open() as f:
        return list(csv.DictReader(f))


def _mean(xs: list[float]) -> float:
    return statistics.mean(xs) if xs else 0.0


def _median(xs: list[float]) -> float:
    return statistics.median(xs) if xs else 0.0


def _stdev(xs: list[float]) -> float:
    return statistics.stdev(xs) if len(xs) > 1 else 0.0


def collect_bioq_results(bioq_root: Path) -> dict:
    """Collect all bioq results into a nested dict:
    {svc: {N: {rep: {meta, timings}}}}"""
    results = {}
    for svc_cfg in SERVICES:
        svc = svc_cfg["name"]
        svc_dir = bioq_root / svc
        if not svc_dir.exists():
            continue
        results[svc] = {}
        for N in BATCH_SIZES:
            n_dir = svc_dir / f"N_{N}"
            if not n_dir.exists():
                continue
            results[svc][N] = {}
            for rep in range(1, REPLICATES + 1):
                rep_dir = n_dir / f"rep_{rep}"
                if not rep_dir.exists():
                    continue
                results[svc][N][rep] = {
                    "meta": _read_meta(rep_dir),
                    "timings": _read_timing(rep_dir),
                }
    return results


def compute_single_job_stats(bioq: dict) -> dict:
    """Median single-job time per service from the N=1 FC runs.

    This is the serial baseline: a single worker finishing N jobs takes
    N × single-job-time. Falls back to config short_per_job_s when a service
    has no N=1 data collected yet.
    """
    stats = {}
    for svc_cfg in SERVICES:
        svc = svc_cfg["name"]
        times = []
        if svc in bioq and 1 in bioq[svc]:
            for rep in bioq[svc][1].values():
                for t in rep["timings"]:
                    try:
                        times.append(float(t["t_completed"]) - float(t["t_submit"]))
                    except (ValueError, KeyError):
                        pass
        stats[svc] = {
            "median_single_s": round(_median(times), 2) if times else svc_cfg["short_per_job_s"],
            "n_single": len(times),
        }
    return stats


def _job_cold_start_s(t: dict) -> float | None:
    """Per-job cold-start overhead (submit -> running).

    When the running transition wasn't observed (the 5 s poll interval is too
    coarse for fast jobs), falls back to the full per-job latency
    ``t_completed - t_submit`` as a conservative upper bound, matching
    plot_aliyun.py and the documented metric.
    """
    try:
        t_submit = float(t["t_submit"])
        t_completed = float(t["t_completed"])
        t_running_s = t.get("t_running", "").strip()
        t_running = float(t_running_s) if t_running_s else t_completed
        overhead = t_running - t_submit
        return overhead if overhead >= 0 else None
    except (ValueError, KeyError):
        return None


def compute_throughput_table(bioq: dict, single_stats: dict) -> list[dict]:
    """Build a row per (svc, N, rep) with throughput, makespan, speedup."""
    rows = []

    for svc_cfg in SERVICES:
        svc = svc_cfg["name"]
        single_s = single_stats[svc]["median_single_s"]

        for N in BATCH_SIZES:
            if svc not in bioq or N not in bioq[svc]:
                continue
            for rep, data in bioq[svc][N].items():
                meta = data["meta"]
                timings = data["timings"]
                makespan = meta.get("makespan_s", 0)
                n_completed = meta.get("n_completed", 0)
                peak_concurrency = meta.get("peak_concurrency", 0)

                # Throughput: completed jobs / makespan (hours)
                throughput = (n_completed / makespan * 3600) if makespan > 0 else 0

                # Speedup vs serial: serial makespan = N × single-job time
                serial_est = N * single_s
                speedup = (serial_est / makespan) if makespan > 0 else 0

                # Cold-start overhead (per-job median, with latency fallback)
                overheads = []
                for t in timings:
                    ov = _job_cold_start_s(t)
                    if ov is not None:
                        overheads.append(ov)
                cold_start = round(_median(overheads), 2) if overheads else 0.0

                rows.append({
                    "svc": svc, "tier": svc_cfg["tier"], "N": N, "rep": rep,
                    "makespan_s": round(makespan, 2),
                    "throughput_jobs_per_hour": round(throughput, 1),
                    "speedup_vs_serial": round(speedup, 2),
                    "peak_concurrency": peak_concurrency,
                    "n_completed": n_completed,
                    "cold_start_s": cold_start,
                    "serial_est_s": round(serial_est, 1),
                })

    return rows


def compute_summary(rows: list[dict]) -> dict:
    """Aggregate across replicates for each (svc, N)."""
    summary = {}
    for svc_cfg in SERVICES:
        svc = svc_cfg["name"]
        summary[svc] = {}
        for N in BATCH_SIZES:
            svc_rows = [r for r in rows if r["svc"] == svc and r["N"] == N]
            if not svc_rows:
                continue
            makespans = [r["makespan_s"] for r in svc_rows]
            throughputs = [r["throughput_jobs_per_hour"] for r in svc_rows]
            speedups = [r["speedup_vs_serial"] for r in svc_rows]
            concurrencies = [r["peak_concurrency"] for r in svc_rows]
            cold_starts = [r["cold_start_s"] for r in svc_rows if r["cold_start_s"] > 0]

            summary[svc][N] = {
                "n_replicates": len(svc_rows),
                "makespan_mean_s": round(_mean(makespans), 2),
                "makespan_std_s": round(_stdev(makespans), 2),
                "makespan_values": [round(m, 2) for m in makespans],
                "throughput_mean_jobs_per_hour": round(_mean(throughputs), 1),
                "throughput_std_jobs_per_hour": round(_stdev(throughputs), 1),
                "speedup_mean": round(_mean(speedups), 2),
                "speedup_std": round(_stdev(speedups), 2),
                "peak_concurrency_mean": round(_mean(concurrencies), 1),
                "peak_concurrency_max": max(concurrencies) if concurrencies else 0,
                "cold_start_mean_s": round(_mean(cold_starts), 2) if cold_starts else 0,
            }
    return summary


# ---------------------------------------------------------------------------
# Statistical tests (each metric compared across batch sizes N)
# ---------------------------------------------------------------------------

def _describe(values: list[float]) -> dict:
    xs = sorted(float(v) for v in values)
    return {
        "n": len(xs),
        "median": round(_median(xs), 3),
        "mean": round(_mean(xs), 3),
        "values": [round(x, 3) for x in xs],
    }


def _mannwhitney(a: list[float], b: list[float]) -> dict | None:
    """Two-sided Mann-Whitney U test (exact permutation, asymptotic fallback).

    Non-parametric — appropriate here because N has only 3 replicates per group
    and latency/cold-start data are skewed with occasional stalls. Returns None
    when a group has <2 observations or there is no variance to test against.
    """
    a = [float(x) for x in a]
    b = [float(x) for x in b]
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return None
    if len(set(a + b)) <= 1:
        return None
    try:
        res = _sp.mannwhitneyu(a, b, alternative="two-sided", method="exact")
        method = "exact"
    except (ValueError, MemoryError):
        res = _sp.mannwhitneyu(a, b, alternative="two-sided", method="asymptotic")
        method = "asymptotic"
    u = float(res.statistic)
    p = float(res.pvalue)
    # rank-biserial correlation: +1 = a entirely above b, -1 = a entirely below b
    r = 1.0 - 2.0 * u / (na * nb)
    return {
        "U": round(u, 4),
        "p_value": p,
        "rank_biserial_r": round(r, 4),
        "n_a": na,
        "n_b": nb,
        "method": method,
    }


def _kruskal(groups: dict) -> dict | None:
    """Kruskal-Wallis H test across N levels (chi-square approximation)."""
    samples = [g for g in groups.values() if len(g) >= 2]
    if len(samples) < 2:
        return None
    pooled = [x for g in samples for x in g]
    if len(set(pooled)) <= 1:
        return None
    try:
        h, p = _sp.kruskal(*samples)
    except ValueError:  # e.g. all numbers identical
        return None
    n = len(pooled)
    k = len(samples)
    # Eta-squared effect size for Kruskal-Wallis: (H - k + 1) / (n - k)
    eta2 = (h - k + 1) / (n - k) if n > k else None
    return {
        "statistic_H": round(float(h), 4),
        "p_value": float(p),
        "eta_squared": round(eta2, 4) if eta2 is not None else None,
        "n_groups": k,
        "n": n,
    }


def _group_by_N(rows: list[dict], svc: str, metric: str) -> dict:
    groups: dict = {}
    for r in rows:
        if r["svc"] != svc or r["N"] is None:
            continue
        groups.setdefault(int(r["N"]), []).append(float(r[metric]))
    return {n: g for n, g in groups.items() if g}


def _run_n_tests(grouped: dict) -> dict | None:
    """Run omnibus (Kruskal-Wallis) + pairwise (Mann-Whitney U) across N levels."""
    if len(grouped) < 2:
        return None
    # Nothing to test if every observation across all N is identical.
    if len(set(x for g in grouped.values() for x in g)) <= 1:
        return None
    ns = sorted(grouped.keys())
    result: dict = {"groups": {str(n): _describe(grouped[n]) for n in ns}}

    om = _kruskal({str(n): grouped[n] for n in ns})
    if om is None:
        result["omnibus"] = {"note": "degenerate — no variance across N"}
    else:
        om["significant"] = om["p_value"] < ALPHA
        result["omnibus"] = om

    pairwise = []
    for i in range(len(ns)):
        for j in range(i + 1, len(ns)):
            mw = _mannwhitney(grouped[ns[i]], grouped[ns[j]])
            if mw is None:
                continue
            mw.update({"a": ns[i], "b": ns[j], "significant": mw["p_value"] < ALPHA})
            pairwise.append(mw)
    result["pairwise"] = pairwise
    return result


def _collect_job_metrics(bioq: dict) -> dict:
    """Pool per-job values by (svc, N): {svc: {N: {cold_start_s:[], latency_s:[]}}}"""
    out: dict = {}
    for svc, n_data in bioq.items():
        out[svc] = {}
        for N, rep_data in n_data.items():
            cold, lat = [], []
            for rep in rep_data.values():
                for t in rep["timings"]:
                    cs = _job_cold_start_s(t)
                    if cs is not None:
                        cold.append(cs)
                    try:
                        l = float(t["t_completed"]) - float(t["t_submit"])
                        if l > 0:
                            lat.append(l)
                    except (ValueError, KeyError):
                        pass
            out[svc][int(N)] = {"cold_start_s": cold, "latency_s": lat}
    return out


def build_statistical_tests(rows: list[dict], bioq: dict) -> dict | None:
    """Compare each metric across N, per service, at two levels of aggregation."""
    if _sp is None:
        print("scipy not available — skipping statistical tests (tables still written)")
        return None

    services = sorted({r["svc"] for r in rows})
    report: dict = {
        "meta": {
            "alpha": ALPHA,
            "tests": {
                "kruskal_wallis": "omnibus across N levels (chi-square approximation, tie-corrected)",
                "mann_whitney_u": "two-sided pairwise between N levels (exact permutation; asymptotic fallback)",
            },
            "effect_sizes": {
                "rank_biserial_r": "Mann-Whitney: 1 - 2U/(n_a*n_b); +1/-1 = full separation",
                "eta_squared": "Kruskal-Wallis: (H - k + 1)/(n - k)",
            },
            "caveats": [
                "replicate_level uses n=3 per N: an exact two-sided Mann-Whitney p "
                "has a floor of 0.1 for n=3 vs n=3, so pairwise p-values can look "
                "flat — the job_level tests carry the signal for per-job metrics.",
                "job_level pools jobs across the 3 replicates of each N; jobs within "
                "a replicate batch share contention, so treat these as exploratory.",
                "p-values are two-sided and uncorrected for multiple comparisons.",
            ],
        },
        "replicate_level": {},
        "job_level": {},
    }

    for svc in services:
        svc_rep = {}
        for metric in REPLICATE_METRICS:
            res = _run_n_tests(_group_by_N(rows, svc, metric))
            if res is not None:
                svc_rep[metric] = res
        if svc_rep:
            report["replicate_level"][svc] = svc_rep

    job_data = _collect_job_metrics(bioq)
    for svc in services:
        if svc not in job_data:
            continue
        svc_job = {}
        for metric in JOB_METRICS:
            grouped = {
                n: job_data[svc][n][metric]
                for n in sorted(job_data[svc])
                if job_data[svc][n][metric]
            }
            res = _run_n_tests(grouped)
            if res is not None:
                svc_job[metric] = res
        if svc_job:
            report["job_level"][svc] = svc_job

    return report


def _flatten_stats(report: dict) -> list[dict]:
    """Flatten the nested report into one row per test for CSV output."""
    rows = []
    for unit in ("replicate_level", "job_level"):
        for svc, svc_data in report.get(unit, {}).items():
            for metric, m_data in svc_data.items():
                om = m_data.get("omnibus", {})
                if isinstance(om, dict) and "statistic_H" in om:
                    rows.append({
                        "unit": unit, "svc": svc, "metric": metric,
                        "test": "kruskal_wallis", "a": "", "b": "",
                        "statistic": om["statistic_H"],
                        "p_value": om["p_value"],
                        "effect_size": om.get("eta_squared", ""),
                        "effect_name": "eta_squared",
                        "n": om.get("n", ""),
                        "significant": om.get("significant", ""),
                    })
                for mw in m_data.get("pairwise", []):
                    rows.append({
                        "unit": unit, "svc": svc, "metric": metric,
                        "test": "mann_whitney_u", "a": mw["a"], "b": mw["b"],
                        "statistic": mw["U"],
                        "p_value": mw["p_value"],
                        "effect_size": mw["rank_biserial_r"],
                        "effect_name": "rank_biserial_r",
                        "n": f"{mw['n_a']},{mw['n_b']}",
                        "significant": mw.get("significant", ""),
                    })
    return rows


def _pw(pairwise: list[dict], a: int, b: int) -> dict:
    for x in pairwise:
        if x.get("a") == a and x.get("b") == b:
            return x
    return {}


def _gstat(groups: dict, n: int, field: str):
    g = groups.get(str(n), {})
    return g.get(field, "")


def build_condensed_table(report: dict) -> list[dict]:
    """Condense the full stats report to one row per (unit, svc, metric):
    medians per N + Kruskal-Wallis omnibus + the two headline pairwise MW tests."""
    rows = []
    for unit in ("replicate_level", "job_level"):
        for svc, svc_data in report.get(unit, {}).items():
            for metric, m_data in svc_data.items():
                groups = m_data.get("groups", {})
                om = m_data.get("omnibus", {})
                p1_50 = _pw(m_data.get("pairwise", []), 1, 50)
                p10_50 = _pw(m_data.get("pairwise", []), 10, 50)
                rows.append({
                    "unit": unit,
                    "svc": svc,
                    "metric": metric,
                    "n_N1": _gstat(groups, 1, "n"),
                    "median_N1": _gstat(groups, 1, "median"),
                    "n_N10": _gstat(groups, 10, "n"),
                    "median_N10": _gstat(groups, 10, "median"),
                    "n_N50": _gstat(groups, 50, "n"),
                    "median_N50": _gstat(groups, 50, "median"),
                    "KW_H": om.get("statistic_H", ""),
                    "KW_p": om.get("p_value", ""),
                    "MW_1vs50_U": p1_50.get("U", ""),
                    "MW_1vs50_p": p1_50.get("p_value", ""),
                    "MW_1vs50_r": p1_50.get("rank_biserial_r", ""),
                    "MW_10vs50_U": p10_50.get("U", ""),
                    "MW_10vs50_p": p10_50.get("p_value", ""),
                    "MW_10vs50_r": p10_50.get("rank_biserial_r", ""),
                })
    return rows


def _render_table_s2_md(rows: list[dict]) -> str:
    """Render the condensed table as markdown, one sub-table per aggregation level."""
    head = [
        "# Table S2 — metric vs batch size N (non-parametric tests)",
        "",
        "Two-sided, uncorrected p-values. K-W = Kruskal–Wallis omnibus across N; "
        "MW = Mann–Whitney U pairwise (rank-biserial r). Replicate level uses n=3 "
        "per N (exact pairwise p floors at 0.10); job level pools per-job cold-start "
        "/ latency across the 3 replicates of each N.",
        "",
    ]

    def _med_n(r, n):
        m = r[f"median_{n}"]
        cnt = r[f"n_{n}"]
        return "—" if m == "" else f"{m:g} ({cnt:g})"

    cols = ["service", "metric", "N=1", "N=10", "N=50",
            "K-W H", "K-W p", "MW 1v50 U", "MW 1v50 p", "MW 1v50 r",
            "MW 10v50 U", "MW 10v50 p", "MW 10v50 r"]

    for unit, heading in (
        ("replicate_level", "Replicate level (unit = replicate)"),
        ("job_level", "Job level (unit = per-job, pooled across replicates)"),
    ):
        unit_rows = [r for r in rows if r["unit"] == unit]
        if not unit_rows:
            continue
        head.append(f"## {heading}")
        head.append("")
        head.append("| " + " | ".join(cols) + " |")
        head.append("|" + "---|" * len(cols))
        for r in unit_rows:
            cells = [
                r["svc"],
                r["metric"],
                _med_n(r, "N1"),
                _med_n(r, "N10"),
                _med_n(r, "N50"),
                _fmt_p(r["KW_H"]) if r["KW_H"] != "" else "—",
                _fmt_p(r["KW_p"]) if r["KW_p"] != "" else "—",
                f"{r['MW_1vs50_U']:g}" if r["MW_1vs50_U"] != "" else "—",
                _fmt_p(r["MW_1vs50_p"]) if r["MW_1vs50_p"] != "" else "—",
                f"{r['MW_1vs50_r']:g}" if r["MW_1vs50_r"] != "" else "—",
                f"{r['MW_10vs50_U']:g}" if r["MW_10vs50_U"] != "" else "—",
                _fmt_p(r["MW_10vs50_p"]) if r["MW_10vs50_p"] != "" else "—",
                f"{r['MW_10vs50_r']:g}" if r["MW_10vs50_r"] != "" else "—",
            ]
            head.append("| " + " | ".join(cells) + " |")
        head.append("")
    return "\n".join(head) + "\n"


def _fmt_p(p) -> str:
    if p is None:
        return ""
    return f"{p:.4g}"


def _print_stats_summary(report: dict) -> None:
    if report is None:
        return
    print("\n=== Statistical tests (across N, uncorrected p) ===")
    for unit in ("replicate_level", "job_level"):
        print(f"\n[{unit}]")
        for svc, svc_data in report.get(unit, {}).items():
            for metric, m_data in svc_data.items():
                om = m_data.get("omnibus", {})
                if isinstance(om, dict) and "p_value" in om:
                    star = "*" if om.get("significant") else ""
                    print(f"  {svc:<14} {metric:<24} omnibus H={om['statistic_H']:<8} "
                          f"p={_fmt_p(om['p_value']):<8}{star}")
                for mw in m_data.get("pairwise", []):
                    star = "*" if mw.get("significant") else ""
                    print(f"    {mw['a']} vs {mw['b']:<4} U={mw['U']:<8} "
                          f"p={_fmt_p(mw['p_value']):<8} r={mw['rank_biserial_r']:<7}{star}")
    print("\n(*) p < 0.05")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bioq", default=str(HERE / "results" / "bioq"))
    args = ap.parse_args()

    bioq_root = Path(args.bioq)

    DATA.mkdir(parents=True, exist_ok=True)

    bioq = collect_bioq_results(bioq_root)

    if not bioq:
        print("No results found — run collect_bioq.py on ECS first, or use make_mock.py")
        return

    # Compute single-job stats (serial baseline)
    single_stats = compute_single_job_stats(bioq)
    (DATA / "single_job_stats.json").write_text(json.dumps(single_stats, indent=2))
    print("\n=== Single-job timing stats (serial baseline) ===")
    for svc, s in single_stats.items():
        print(f"  {svc}: median={s['median_single_s']}s (n={s['n_single']})")

    # Build throughput table
    rows = compute_throughput_table(bioq, single_stats)

    # Write CSV
    cols = ["svc", "tier", "N", "rep", "makespan_s",
            "throughput_jobs_per_hour", "speedup_vs_serial",
            "peak_concurrency", "n_completed", "cold_start_s",
            "serial_est_s"]
    csv_path = DATA / "throughput.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {csv_path.relative_to(HERE)} ({len(rows)} rows)")

    # Write summary
    summary = compute_summary(rows)
    summary_path = DATA / "scaling_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))
    print(f"Wrote {summary_path.relative_to(HERE)}")

    # Statistical tests
    stats_report = build_statistical_tests(rows, bioq)
    if stats_report is not None:
        st_path = DATA / "statistical_tests.json"
        st_path.write_text(json.dumps(stats_report, indent=2))
        print(f"Wrote {st_path.relative_to(HERE)}")

        flat = _flatten_stats(stats_report)
        flat_path = DATA / "statistical_tests.csv"
        flat_cols = ["unit", "svc", "metric", "test", "a", "b", "statistic",
                     "p_value", "effect_size", "effect_name", "n", "significant"]
        with flat_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=flat_cols, extrasaction="ignore")
            w.writeheader()
            for row in flat:
                row = dict(row)
                row["p_value"] = _fmt_p(row["p_value"])
                w.writerow(row)
        print(f"Wrote {flat_path.relative_to(HERE)} ({len(flat)} tests)")

        s2 = build_condensed_table(stats_report)
        s2_path = DATA / "table_s2.csv"
        s2_cols = ["unit", "svc", "metric",
                   "n_N1", "median_N1", "n_N10", "median_N10", "n_N50", "median_N50",
                   "KW_H", "KW_p",
                   "MW_1vs50_U", "MW_1vs50_p", "MW_1vs50_r",
                   "MW_10vs50_U", "MW_10vs50_p", "MW_10vs50_r"]
        with s2_path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=s2_cols, extrasaction="ignore")
            w.writeheader()
            for row in s2:
                row = dict(row)
                row["KW_p"] = _fmt_p(row["KW_p"]) if row["KW_p"] != "" else ""
                row["MW_1vs50_p"] = _fmt_p(row["MW_1vs50_p"]) if row["MW_1vs50_p"] != "" else ""
                row["MW_10vs50_p"] = _fmt_p(row["MW_10vs50_p"]) if row["MW_10vs50_p"] != "" else ""
                w.writerow(row)
        print(f"Wrote {s2_path.relative_to(HERE)} ({len(s2)} rows)")

        s2_md_path = DATA / "table_s2.md"
        s2_md_path.write_text(_render_table_s2_md(s2))
        print(f"Wrote {s2_md_path.relative_to(HERE)}")

    # Print summary table
    print("\n=== Scaling summary ===")
    print(f"{'svc':<18} {'N':<6} {'makespan(s)':<16} {'throughput/hr':<18} {'speedup':<12} {'peak_conc':<10}")
    print("-" * 80)
    for svc, svc_summary in summary.items():
        for N in BATCH_SIZES:
            if N not in svc_summary:
                continue
            s = svc_summary[N]
            print(f"{svc:<18} {N:<6} "
                  f"{s['makespan_mean_s']:>8.1f} ±{s['makespan_std_s']:>5.1f}  "
                  f"{s['throughput_mean_jobs_per_hour']:>10.1f} ±{s['throughput_std_jobs_per_hour']:>6.1f}  "
                  f"{s['speedup_mean']:>6.2f} ±{s['speedup_std']:>4.2f}  "
                  f"{s['peak_concurrency_mean']:>4.0f} (max {s['peak_concurrency_max']})")

    if stats_report is not None:
        _print_stats_summary(stats_report)


if __name__ == "__main__":
    main()