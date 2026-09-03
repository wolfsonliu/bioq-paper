"""Throughput-scaling config (single source of truth).

Defines the two services, batch sizes, inputs, params, and image tags.
Stdlib-only so collectors run on a bare ECS host (python3 + bioq + docker).
"""
from __future__ import annotations

# Harbor registry
REGISTRY = ""

# Batch sizes to test (max 50 — Aliyun FC GPU instance quota ceiling)
BATCH_SIZES = [1, 10, 50]

# Replicates per (service, N) point
REPLICATES = 3

# Poll interval for bioq status checks (seconds)
POLL_INTERVAL = 5.0

# Poll timeout per job (seconds)
POLL_TIMEOUT = 7200.0

# Seconds to wait between replicates (let FC instances cool down / release)
COOLDOWN = 1200

# If True, run a throwaway warm-up batch before the first recorded replicate.
WARM_UP = True

# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

SERVICES = [
    # ---- Hot tier: fast, GPU ----
    {
        "name": "proteinmpnn",
        "endpoint": "design",
        "tier": "hot",
        "gpu": True,
        "image": f"{REGISTRY}/proteinmpnn-server:v0.0.15",
        "short_per_job_s": 120,           # expected single-job seconds
        "files": {"pdb": "5L33.pdb"},
        "params": {
            "num_seq_per_target": 2,
            "sampling_temp": 0.1,
            "model_variant": "vanilla",
            "model_name": "v_48_020",
        },
        "seed_start": 1,
    },
    {
        "name": "mmseqs2",
        "endpoint": "msa",
        "tier": "hot",
        "gpu": True,
        "image": f"{REGISTRY}/mmseqs2-server:v0.0.6",
        "short_per_job_s": 60,            # fast MSA search
        "files": {"q": "sequence.fasta"},
        "params": {"mode": "env"},
        "seed_start": None,
    },
    # ---- Warm tier: medium, GPU ----
    {
        "name": "rfdiffusion2",
        "endpoint": "custom",
        "tier": "warm",
        "gpu": True,
        "image": f"{REGISTRY}/rfdiffusion2-server:v0.0.19",
        "short_per_job_s": 480,           # heavier protein generation
        "files": {},
        "params": {
            "contigs": "150",
            "num_designs": 1,
        },
        "seed_start": 1,
    },
    {
        "name": "rfdiffusion",
        "endpoint": "unconditional",
        "tier": "warm",
        "gpu": True,
        "image": f"{REGISTRY}/rfdiffusion-server:v0.0.11",
        "short_per_job_s": 120,           # unconditional backbone generation
        "files": {},
        "params": {
            "num_designs": 1,
            "diffuser_t": 25,
            "min_length": 100,
            "max_length": 100,
        },
        "seed_start": None,
    },
    {
        "name": "boltz",
        "endpoint": "predict_structure",
        "tier": "warm",
        "gpu": True,
        "image": f"{REGISTRY}/boltz-server:v0.0.12",
        "short_per_job_s": 300,           # structure prediction
        "files": {},
        "params": {
            "msa_mode": "empty",
            "diffusion_samples": 1,
            "recycling_steps": 1,
            "sampling_steps": 50,
        },
        "set_json": {
            "sequences": '[{"type": "protein", "id": "A", "sequence": "MKTAYIAKQRQISFVKSHFSRQLE", "msa_uri": "empty"}]',
        },
        "seed_start": None,
    },
    {
        "name": "boltzgen",
        "endpoint": "design",
        "tier": "warm",
        "gpu": True,
        "image": f"{REGISTRY}/boltzgen-server:v0.0.13",
        "short_per_job_s": 300,           # protein design via Boltz
        "files": {"design_yaml": "vanilla.yaml"},
        "params": {
            "protocol": "protein-anything",
            "num_designs": 5,
            "budget": 5,
        },
        "seed_start": None,
    },
    {
        "name": "alphafold",
        "endpoint": "fold",
        "tier": "warm",
        "gpu": True,
        "image": f"{REGISTRY}/alphafold-server:v0.0.5",
        "short_per_job_s": 600,           # structure prediction (heaviest)
        "files": {"input_fasta": "bench.fasta"},
        "params": {
            "models_to_relax": "none",
        },
        "seed_start": None,
    },
    {
        "name": "reinvent",
        "endpoint": "sampling",
        "tier": "warm",
        "gpu": True,
        "image": f"{REGISTRY}/reinvent-server:v0.0.5",
        "short_per_job_s": 60,            # molecule generation
        "files": {},
        "params": {
            "generator": "reinvent",
            "num_smiles": 100,
            "temperature": 1.0,
        },
        "seed_start": None,
    },
    # ---- Cold tier: fast, CPU ----
    {
        "name": "plip",
        "endpoint": "profile",
        "tier": "cold",
        "gpu": False,
        "image": f"{REGISTRY}/plip-server:v0.0.1",
        "short_per_job_s": 10,            # fast interaction profiling
        "files": {"input_pdb": "1vsn.pdb"},
        "params": {"mode": "default"},
        "seed_start": None,
    },
    {
        "name": "dockq",
        "endpoint": "score",
        "tier": "cold",
        "gpu": False,
        "image": f"{REGISTRY}/dockq-server:v0.0.12",
        "short_per_job_s": 5,             # very fast scoring
        "files": {"model": "model.pdb", "native": "native.pdb"},
        "params": {},
        "seed_start": None,
    },
]

# ---------------------------------------------------------------------------
# Derived helpers
# ---------------------------------------------------------------------------

def svc_config(name: str) -> dict:
    for s in SERVICES:
        if s["name"] == name:
            return s
    raise ValueError(f"unknown service {name!r}")
