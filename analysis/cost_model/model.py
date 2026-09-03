#!/usr/bin/env python3
"""Cost model: compute $/job, break-even duty cycle, sensitivity sweep.

Reads service profiles from config.py (or the throughput-scaling analysis's single_job_stats.json) and
produces three outputs:

  data/cost_table.csv       — $/job per service, per GPU class
  data/break_even.json      — break-even duty cycle d* for each GPU class
  data/sensitivity.json     — sensitivity sweep: d* across GPU price ±X% and job mix

Usage:
    python3 model.py                        # uses config defaults
    python3 model.py --throughput-data path         # inject measured times from the throughput-scaling analysis
    python3 model.py --mock                 # generate mock data, then model

Stdlib-only for core math; needs json/csv for output.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import config  # noqa: E402


def _load_e3_single_job_stats(path: Path) -> dict[str, float]:
    """Load the throughput-scaling analysis's single_job_stats.json -> {service: median single-job seconds}.

    That analysis's real format is ``{service: {"median_single_s": float, "n_single": int}}``.
    Rows with ``n_single == 0`` are its unmeasured config fallbacks (services that
    were never actually run), so they are skipped and never override a profile.
    Also accepts the flat ``{service: float}`` mock format for self-testing.
    """
    with open(path) as f:
        data = json.load(f)
    out: dict[str, float] = {}
    if isinstance(data, list):
        for d in data:
            sec = d.get("median_gpu_sec", d.get("median_single_s"))
            if sec is not None:
                out[d["service"]] = float(sec)
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, dict):
                if int(v.get("n_single", 1)) <= 0:
                    continue
                sec = v.get("median_single_s", v.get("median_gpu_sec"))
                if sec is None:
                    continue
                out[k] = float(sec)
            else:
                out[k] = float(v)
    else:
        raise ValueError(f"unexpected throughput-scaling data format in {path}")
    return out


def _load_profiles(e3_path: Path | None) -> list[config.ServiceProfile]:
    """Load service profiles, optionally overriding gpu_sec_per_job from the throughput-scaling data."""
    profiles = [config.ServiceProfile(**p.__dict__) for p in config.DEFAULT_SERVICE_PROFILES]
    if e3_path is not None and e3_path.is_file():
        e3 = _load_e3_single_job_stats(e3_path)
        for p in profiles:
            # The throughput-scaling keys are bare ("proteinmpnn"); our profiles are suffixed
            # ("proteinmpnn-server"). Match both spellings.
            bare = p.name.removesuffix("-server")
            key = p.name if p.name in e3 else (bare if bare in e3 else None)
            if key is not None:
                p.gpu_sec_per_job = e3[key]
                print(f"  [scale] {p.name}: {p.gpu_sec_per_job:.1f} GPU-seconds (from throughput-scaling '{key}')")
            else:
                print(f"  [cfg] {p.name}: {p.gpu_sec_per_job:.1f} GPU-seconds (not in throughput-scaling data)")
    else:
        for p in profiles:
            print(f"  [cfg] {p.name}: {p.gpu_sec_per_job:.1f} GPU-seconds (default)")
    return profiles


def compute_job_cost(profiles: list[config.ServiceProfile],
                     fc_rate: config.FcGpuRate,
                     cold_start: float = config.COLD_START_OVERHEAD_SEC,
                     ) -> list[dict]:
    """Compute $/job per service for a given FC GPU rate.

    Returns list of dicts with keys: service, gpu_class, gpu_sec, billable_sec,
    usd_per_job, usd_per_1000_jobs, jobs_per_month, usd_per_month.
    """
    rows = []
    for p in profiles:
        billable = p.gpu_sec_per_job + cold_start
        usd = billable * fc_rate.usd_per_gpu_sec
        rows.append({
            "service": p.name,
            "gpu_class": p.gpu_class,
            "gpu_sec_per_job": round(p.gpu_sec_per_job, 1),
            "billable_sec_per_job": round(billable, 1),
            "usd_per_job": round(usd, 6),
            "usd_per_1000_jobs": round(usd * 1000, 4),
            "jobs_per_month_typical": p.jobs_per_month_typical,
            "usd_per_month_typical": round(usd * p.jobs_per_month_typical, 2),
        })
    return rows


def compute_break_even(
    profiles: list[config.ServiceProfile],
    fc_rate: config.FcGpuRate,
    dedicated_cost: config.DedicatedGpuCost,
    job_mix: dict[str, float] | None = None,
    cold_start: float = config.COLD_START_OVERHEAD_SEC,
    monthly_jobs: int = 1000,
) -> dict:
    """Compute break-even duty cycle d*.

    Args:
        profiles: service profiles
        fc_rate: FC GPU rate
        dedicated_cost: dedicated GPU cost model
        job_mix: dict of service_name -> weight (fraction of jobs).
                 If None, uniform mix.
        cold_start: cold-start overhead seconds per job
        monthly_jobs: total monthly job volume at 100 % duty cycle
                      (the d=1 reference point)

    Returns dict with break-even metrics.
    """
    # Weighted-average $/job across the mix
    if job_mix is None:
        job_mix = {p.name: 1.0 / len(profiles) for p in profiles}

    wavg_job_cost = 0.0
    wavg_gpu_sec = 0.0
    for p in profiles:
        weight = job_mix.get(p.name, 0.0)
        if weight == 0:
            continue
        billable = p.gpu_sec_per_job + cold_start
        usd = billable * fc_rate.usd_per_gpu_sec
        wavg_job_cost += weight * usd
        wavg_gpu_sec += weight * p.gpu_sec_per_job

    # Dedicated monthly cost (amortized purchase)
    dedicated_monthly = config.monthly_amortized(
        dedicated_cost.purchase_usd, dedicated_cost.lifetime_years
    )
    # Cloud VM monthly cost (24/7)
    cloud_monthly = dedicated_cost.cloud_vm_usd_per_hour * 730.5

    # Break-even: serverless_cost = dedicated_cost
    # serverless_cost = monthly_jobs * wavg_job_cost * d
    #   where d = duty cycle = fraction of wall-clock the GPU is computing
    #   monthly_jobs = max jobs at d=1 (GPU 100% busy)
    # At d=1: max_jobs = (30 * 24 * 3600) / wavg_gpu_sec (monthly seconds / sec per job)
    max_jobs_per_month = (30 * 24 * 3600) / wavg_gpu_sec if wavg_gpu_sec > 0 else 1

    def serverless_cost(d: float) -> float:
        return max_jobs_per_month * d * wavg_job_cost

    # Find d* where serverless_cost(d) = dedicated_monthly
    if dedicated_monthly <= 0:
        break_even_d = 1.0
    else:
        break_even_d = min(1.0, dedicated_monthly / serverless_cost(1.0))

    # Cloud VM break-even
    if cloud_monthly <= 0:
        break_even_d_cloud = 1.0
    else:
        break_even_d_cloud = min(1.0, cloud_monthly / serverless_cost(1.0))

    return {
        "gpu_class": fc_rate.gpu_class,
        "fc_rate_usd_per_sec": fc_rate.usd_per_gpu_sec,
        "fc_rate_cny_per_sec": fc_rate.cny_per_gpu_sec,
        "cu_per_gpu_sec": fc_rate.cu_per_gpu_sec,
        "vram_gb": fc_rate.vram_gb,
        "series": fc_rate.series,
        "dedicated_purchase_usd": dedicated_cost.purchase_usd,
        "dedicated_lifetime_years": dedicated_cost.lifetime_years,
        "dedicated_monthly_usd": round(dedicated_monthly, 2),
        "cloud_vm_monthly_usd": round(cloud_monthly, 2),
        "wavg_job_cost_usd": round(wavg_job_cost, 6),
        "wavg_gpu_sec_per_job": round(wavg_gpu_sec, 1),
        "max_jobs_per_month_at_d1": round(max_jobs_per_month),
        "break_even_duty_cycle": round(break_even_d, 4),
        "break_even_duty_cycle_pct": round(break_even_d * 100, 2),
        "break_even_duty_cycle_cloud_vm": round(break_even_d_cloud, 4),
        "break_even_duty_cycle_cloud_vm_pct": round(break_even_d_cloud * 100, 2),
    }


def sensitivity_sweep(
    profiles: list[config.ServiceProfile],
    fc_rate: config.FcGpuRate,
    dedicated_cost: config.DedicatedGpuCost,
    price_pcts: list[float] | None = None,
    mix_scenarios: list[tuple[str, dict[str, float]]] | None = None,
) -> dict:
    """Sweep GPU price ±X% and job mix scenarios.

    Returns dict: {scenario: {price_pct: break_even_d}}.
    """
    if price_pcts is None:
        price_pcts = config.GPU_PRICE_SENSITIVITY_PCT
    if mix_scenarios is None:
        mix_scenarios = config.JOB_MIX_SENSITIVITY_SCENARIOS

    results: dict = {}
    for mix_name, job_mix in mix_scenarios:
        for pct in price_pcts:
            # Adjust FC rate by price_pct
            adj_rate = config.FcGpuRate(
                gpu_class=fc_rate.gpu_class,
                usd_per_gpu_sec=fc_rate.usd_per_gpu_sec * (1 + pct / 100),
                description=fc_rate.description,
            )
            be = compute_break_even(profiles, adj_rate, dedicated_cost, job_mix=job_mix)
            key = f"{mix_name}_{pct:+.0f}pct"
            results[key] = {
                "mix": mix_name,
                "price_pct": pct,
                "break_even_d": be["break_even_duty_cycle"],
                "wavg_job_cost_usd": be["wavg_job_cost_usd"],
            }
    return results


def run(data_dir: Path, e3_path: Path | None, mock: bool) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)

    print("=== Cost Model ===")
    print(f"FC rate card: {config.FC_RATE_CARD_DATE.isoformat()}")
    print()

    # --- Load profiles ---
    print("Service profiles:")
    profiles = _load_profiles(e3_path)
    print()

    # --- Per-service cost table ---
    cost_rows: list[dict] = []
    for fc_key in ["T4", "A10", "A100", "H100"]:
        fc_rate = config.FC_GPU_RATES[fc_key]
        # Filter profiles matching this GPU class
        matching = [p for p in profiles if p.gpu_class == fc_key]
        # Also include profiles with mismatched GPUs (show what they'd cost on this GPU)
        # Actually, the paper should show each service on its own GPU class.
        # Let's compute each service on its assigned GPU.
        pass

    # Compute each service on its own GPU class
    for p in profiles:
        fc_rate = config.FC_GPU_RATES[p.gpu_class]
        rows = compute_job_cost([p], fc_rate)
        cost_rows.extend(rows)

    # Write cost table CSV
    cost_path = data_dir / "cost_table.csv"
    with open(cost_path, "w", newline="") as f:
        fieldnames = ["service", "gpu_class", "gpu_sec_per_job", "billable_sec_per_job",
                      "usd_per_job", "usd_per_1000_jobs", "jobs_per_month_typical",
                      "usd_per_month_typical"]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(cost_rows)
    print(f"cost table: {len(cost_rows)} rows -> {cost_path}")

    # --- Compute break-even for each GPU class ---
    be_all: list[dict] = []
    for fc_key in ["T4", "A10", "A100", "H100"]:
        fc_rate = config.FC_GPU_RATES[fc_key]
        dedicated = config.DEDICATED_GPU_COSTS[fc_key]
        profiles_on_gpu = [p for p in profiles if p.gpu_class == fc_key]
        if not profiles_on_gpu:
            continue
        be = compute_break_even(
            profiles_on_gpu, fc_rate, dedicated,
            job_mix={p.name: 1.0 / len(profiles_on_gpu) for p in profiles_on_gpu}
        )
        be_all.append(be)
        print(f"  {fc_key}: break-even d* = {be['break_even_duty_cycle_pct']:.1f}% "
              f"(cloud VM: {be['break_even_duty_cycle_cloud_vm_pct']:.1f}%)")

    # All-services on one GPU (e.g. A100) with default mix
    fc_rate = config.FC_GPU_RATES["A100"]
    dedicated = config.DEDICATED_GPU_COSTS["A100"]
    be_all_services = compute_break_even(
        profiles, fc_rate, dedicated,
        job_mix=config.DEFAULT_JOB_MIX
    )
    print(f"  all on A100 (weighted mix): break-even d* = "
          f"{be_all_services['break_even_duty_cycle_pct']:.1f}%")
    be_all.append(be_all_services)

    # Write break-even JSON
    be_path = data_dir / "break_even.json"
    with open(be_path, "w") as f:
        json.dump(be_all, f, indent=2, ensure_ascii=False)
    print(f"break-even: {len(be_all)} entries -> {be_path}")

    # --- Sensitivity sweep (A100 only) ---
    fc_rate = config.FC_GPU_RATES["A100"]
    dedicated = config.DEDICATED_GPU_COSTS["A100"]
    sens = sensitivity_sweep(profiles, fc_rate, dedicated)
    sens_path = data_dir / "sensitivity.json"
    with open(sens_path, "w") as f:
        json.dump(sens, f, indent=2, ensure_ascii=False)
    print(f"sensitivity: {len(sens)} scenarios -> {sens_path}")

    # --- Summary ---
    print()
    print("=== Summary ===")
    print(f"Rate card: {config.FC_RATE_CARD_DATE.isoformat()}")
    print(f"Cold-start overhead: {config.COLD_START_OVERHEAD_SEC}s")
    for r in cost_rows:
        print(f"  {r['service']:<26} {r['gpu_class']:<5}  "
              f"{r['gpu_sec_per_job']:>8.1f}s  "
              f"${r['usd_per_job']:<.4f}/job  "
              f"${r['usd_per_month_typical']:<.2f}/mo @ {r['jobs_per_month_typical']} jobs/mo")
    print()
    print(f"Break-even (all on A100, weighted mix): "
          f"{be_all_services['break_even_duty_cycle_pct']:.1f}% duty cycle")
    print(f"  → below d*: serverless (FC) wins")
    print(f"  → above d*: dedicated GPU wins")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--throughput-data", type=Path,
                    help="path to the throughput-scaling single_job_stats.json (overrides config defaults)")
    ap.add_argument("--mock", action="store_true",
                    help="generate mock data via make_mock.py first")
    ap.add_argument("--data-dir", type=Path, default=HERE / "data",
                    help="output data directory (default: data/)")
    args = ap.parse_args()

    if args.mock:
        print("  generating mock data via make_mock ...")
        import make_mock  # noqa
        make_mock.main(argv=[])  # empty argv — use defaults, don't inherit parent args

    run(args.data_dir, args.throughput_data, args.mock)


if __name__ == "__main__":
    main()