#!/usr/bin/env python3
"""Single source of truth: pricing assumptions, service catalog, job mix.

All monetary values are in USD. All rates state their source and date so the
model is reproducible when pricing changes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date

# ---------------------------------------------------------------------------
# 1. Function Compute GPU pricing (serverless, CU-billed)
# ---------------------------------------------------------------------------
# Source: `aliyun_fc_price.md` in this directory (Alibaba Cloud FC CU billing),
# synced 2026-08-24. FC no longer bills a flat per-GPU-second rate. Instead:
#   (a) GPU usage — vRAM_GB × active_seconds — converts to CU at a per-series
#       coefficient CU/(GB·s) (active vs "shallow sleep" 浅休眠 idle state).
#   (b) CU is charged on a tiered ladder (yuan/CU).
#   (c) Optionally, keeping an idle instance warm bills the "shallow sleep"
#       coefficient rather than $0. bioq releases instances (scale-to-zero),
#       so the active coefficient is the relevant one; the shallow-sleep idle
#       cost is NOT modelled here (see README.md caveat).
# Non-GPU resources (vCPU, memory, disk, invocations) also bill as CU but are
# not separately priced in the source sheet; we model GPU CU only and state
# this as a caveat.
#
# Currency: the sheet is in CNY (yuan). We convert to USD at a fixed, stated
# assumed rate so the comparison against USD-priced owned GPUs is homogeneous.
# The rate is an assumption, not a measured value — edit CNY_PER_USD freely.

CNY_PER_USD = 6.80           # assumed USD/CNY mid-rate at snapshot (2026-08-24)
USD_PER_CNY = 1.0 / CNY_PER_USD

# CU ladder: (inclusive upper CU bound, yuan per CU).
CU_TIER_PRICING: list[tuple[float, float]] = [
    (1e8,          0.00012),  # tier 1: (0, 1e8] CU
    (5e8,          0.00010),  # tier 2: (1e8, 5e8] CU
    (float("inf"), 0.00008),  # tier 3: >5e8 CU
]
CU_DEFAULT_TIER = 0  # bursty-lab monthly CU stays far below 1e8 → tier 1

# Per-series CU conversion coefficients, CU/(GB·s): {active, shallow_sleep}.
GPU_SERIES_CU: dict[str, dict[str, float]] = {
    "tesla":     {"active": 2.1,  "shallow_sleep": 0.5},
    "ampere":    {"active": 1.8,  "shallow_sleep": 0.3},
    "ada1":      {"active": 1.7,  "shallow_sleep": 0.2},
    "ada23":     {"active": 1.95, "shallow_sleep": 0.23},
    "blackwell": {"active": 2.1,  "shallow_sleep": 0.28},
    "hopper":    {"active": 2.31, "shallow_sleep": 0.315},
    "xpu":       {"active": 1.2,  "shallow_sleep": 0.23},
}


@dataclass(frozen=True)
class FcGpuRate:
    gpu_class: str          # e.g. "T4", "A10", "A100", "H100"
    usd_per_gpu_sec: float  # effective USD per active GPU-second (default tier)
    series: str = ""        # key into GPU_SERIES_CU
    vram_gb: int = 0        # instance vRAM
    cu_per_gpu_sec: float = 0.0   # active CU/s = vRAM_GB × series active coef
    cny_per_gpu_sec: float = 0.0  # active yuan/s = CU/s × tier price
    description: str = ""


def make_fc_gpu_rate(gpu_class: str, series: str, vram_gb: int,
                     description: str = "") -> FcGpuRate:
    """Derive the effective rate for one GPU class from the CU price sheet."""
    cu_per_sec = vram_gb * GPU_SERIES_CU[series]["active"]
    cny_per_sec = cu_per_sec * CU_TIER_PRICING[CU_DEFAULT_TIER][1]
    usd_per_sec = cny_per_sec * USD_PER_CNY
    return FcGpuRate(
        gpu_class=gpu_class,
        usd_per_gpu_sec=usd_per_sec,
        series=series,
        vram_gb=vram_gb,
        cu_per_gpu_sec=round(cu_per_sec, 4),
        cny_per_gpu_sec=round(cny_per_sec, 8),
        description=description,
    )


FC_GPU_RATES: dict[str, FcGpuRate] = {
    "T4":  make_fc_gpu_rate("T4",  "tesla",  16,
                            "T4 (16 GB) — Tesla series, entry GPU"),
    "A10": make_fc_gpu_rate("A10", "ampere", 24,
                            "A10 (24 GB) — Ampere series, mid-range"),
    "A100": make_fc_gpu_rate("A100", "ampere", 40,
                             "A100 (40 GB) — Ampere series, high-end"),
    "H100": make_fc_gpu_rate("H100", "hopper", 80,
                             "H100 (80 GB) — Hopper series, flagship"),
}

FC_RATE_CARD_DATE = date(2026, 8, 24)

# Cold-start overhead: additional billable seconds per invocation (image pull +
# container init). Measured empirically: ~5–15 s for GPU images on Alibaba FC.
COLD_START_OVERHEAD_SEC = 10.0  # conservative mean

# ---------------------------------------------------------------------------
# 2. Dedicated / persistent GPU costs
# ---------------------------------------------------------------------------
# Two models: (a) purchase and amortize, (b) cloud VM hourly rental.
# Source: NVIDIA MSRP, cloud provider list prices, various industry surveys.
# Amortization: 4-year straight-line; 0 residual.

@dataclass(frozen=True)
class DedicatedGpuCost:
    gpu_class: str
    purchase_usd: float      # one-time purchase price (MSRP)
    lifetime_years: float    # useful life before obsolescence
    cloud_vm_usd_per_hour: float  # persistent GPU cloud VM, per hour

DEDICATED_GPU_COSTS: dict[str, DedicatedGpuCost] = {
    "T4":  DedicatedGpuCost("T4",  3000,  4.0, 0.60),
    "A10": DedicatedGpuCost("A10", 5000,  4.0, 0.90),
    "A100":DedicatedGpuCost("A100",15000, 4.0, 2.50),
    "H100":DedicatedGpuCost("H100",30000, 4.0, 5.00),
}

# ---------------------------------------------------------------------------
# 3. Service catalog — mapping service name → GPU class + typical job profile
# ---------------------------------------------------------------------------
# GPU-seconds per job: measured from the throughput-scaling analysis
# (single_job_stats.json). Pre-filled with representative values from
# production runs. The model script reads from the throughput-scaling data when
# available; these are the fallback defaults (and the basis for make_mock.py).

@dataclass
class ServiceProfile:
    name: str               # service name, e.g. "rfdiffusion2-server"
    gpu_class: str          # GPU class key in FC_GPU_RATES / DEDICATED_GPU_COSTS
    gpu_sec_per_job: float  # mean GPU-seconds per successful job (wall-clock)
    jobs_per_month_typical: int = 100  # typical monthly volume for a wet-lab
    tier: str = "hot"       # hot / warm / cold (job frequency class)

# Default profiles (will be updated from the throughput-scaling data when available)
DEFAULT_SERVICE_PROFILES: list[ServiceProfile] = [
    ServiceProfile("rfdiffusion2-server", "A100", 360.0,  200, "hot"),
    ServiceProfile("proteinmpnn-server",  "T4",   90.0,   500, "hot"),
    ServiceProfile("boltz-server",        "A100", 600.0,   50, "warm"),
    ServiceProfile("dockq-server",        "T4",   30.0,   300, "hot"),
    ServiceProfile("diffdock-server",     "A100", 480.0,   30, "warm"),
    ServiceProfile("reinvent-server",     "A10",  1200.0,  10, "cold"),
    ServiceProfile("flowmol-server",      "A10",  300.0,   50, "warm"),
    ServiceProfile("esmfold2-server",     "T4",   180.0,  100, "hot"),
    ServiceProfile("alphafold-server",    "A100", 900.0,   20, "warm"),
    ServiceProfile("genie3-server",       "T4",   60.0,   100, "hot"),
]

# Default job mix weights (for weighted-average $/job calculations)
DEFAULT_JOB_MIX: dict[str, float] = {
    "rfdiffusion2-server": 0.15,
    "proteinmpnn-server":  0.25,
    "boltz-server":        0.05,
    "dockq-server":        0.20,
    "diffdock-server":     0.05,
    "reinvent-server":     0.02,
    "flowmol-server":      0.05,
    "esmfold2-server":     0.10,
    "alphafold-server":    0.03,
    "genie3-server":       0.10,
}

# ---------------------------------------------------------------------------
# 4. Sensitivity sweep defaults
# ---------------------------------------------------------------------------
GPU_PRICE_SENSITIVITY_PCT: list[float] = [-30, -15, 0, 15, 30]  # +/- %
JOB_MIX_SENSITIVITY_SCENARIOS: list[tuple[str, dict[str, float]]] = [
    ("default", DEFAULT_JOB_MIX),
    ("heavy-design", {
        "rfdiffusion2-server": 0.30,
        "diffdock-server":     0.10,
        "boltz-server":        0.10,
        "reinvent-server":     0.05,
        "flowmol-server":      0.10,
        "proteinmpnn-server":  0.15,
        "dockq-server":        0.05,
        "esmfold2-server":     0.05,
        "alphafold-server":    0.05,
        "genie3-server":       0.05,
    }),
    ("heavy-screening", {
        "rfdiffusion2-server": 0.05,
        "proteinmpnn-server":  0.25,
        "dockq-server":        0.35,
        "esmfold2-server":     0.15,
        "genie3-server":       0.15,
        "boltz-server":        0.02,
        "diffdock-server":     0.01,
        "reinvent-server":     0.01,
        "flowmol-server":      0.01,
        "alphafold-server":    0.00,
    }),
]

# ---------------------------------------------------------------------------
# 5. Derived helpers
# ---------------------------------------------------------------------------

def monthly_amortized(purchase_usd: float, lifetime_years: float) -> float:
    """Straight-line monthly amortization."""
    return purchase_usd / (lifetime_years * 12)

def monthly_dedicated_gpu(gpu_class: str) -> float:
    """Monthly cost of owning a dedicated GPU (amortized purchase)."""
    c = DEDICATED_GPU_COSTS[gpu_class]
    return monthly_amortized(c.purchase_usd, c.lifetime_years)

def monthly_dedicated_cloud_vm(gpu_class: str) -> float:
    """Monthly cost of a persistent cloud VM (24/7)."""
    c = DEDICATED_GPU_COSTS[gpu_class]
    return c.cloud_vm_usd_per_hour * 730.5  # avg hours per month