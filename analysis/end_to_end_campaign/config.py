"""rfantibody case — configuration (single source of truth).

Reproduces the RFantibody paper design campaigns (Bennett et al. 2025) across
all VHH and scFv targets listed in Tables 5 and 7 of the Supplementary Methods.

Each target is a dict with the rfdiffusion params required by the
rfantibody-server endpoints.  Stdlib-only so run_campaign.py runs on a bare
ECS host (python3 + bioq).
"""
from __future__ import annotations

SERVICE = "rfantibody"

# Same image deployed to FC (for reference; the bioq campaign path does not
# need it). Override with E5_IMAGE_RFANTIBODY.
IMAGE = "harbor.ruosheng.bio/aliyun_fc/rfantibody-server:v0.2.0"

# Framework PDBs (bundled by fetch_inputs.sh)
VHH_FRAMEWORK = "vhh_nbbcII10.pdb"       # 3DWT chain A (h-NbBcII10FGLA)
SCFV_FRAMEWORK = "hu-4D5-8_Fv.pdb"       # humanized scFv framework

# ---------------------------------------------------------------------------
# VHH design campaigns — Table 5 of the Supplementary Methods
# ---------------------------------------------------------------------------
VHH_TARGETS = [
    {
        "name": "HIV_Env",
        "pdb": "2NY7.pdb",
        "framework": VHH_FRAMEWORK,
        "hotspots": "G371,G375,G435,G475",
        "design_loops": "H1:7,H2:6,H3:5-13",
        "num_designs": 200,          # per the paper
        "diffuser_t": 100,           # increased from 50 — HIV Env is challenging
        "paper_info": {
            "target": "HIV Env (2NY7)",
            "epitope": "CD4-binding site",
            "citation": "Bennett et al., Table 5",
        },
    },
    {
        "name": "SARS_CoV2_RBD",
        "pdb": "6M0J.pdb",
        "framework": VHH_FRAMEWORK,
        "hotspots": "E492,E493,E494,E495,E496,E497",
        "design_loops": "H1:7,H2:6,H3:5-13",
        "num_designs": 200,
        "diffuser_t": 50,
        "paper_info": {
            "target": "SARS-CoV-2 RBD (6M0J)",
            "epitope": "receptor-binding motif",
            "citation": "Bennett et al., Table 5",
        },
    },
    {
        "name": "RSV_Site_I",
        "pdb": "7LVW.pdb",
        "framework": VHH_FRAMEWORK,
        "hotspots": "D469,D384",
        "design_loops": "H1:7,H2:6,H3:5-13",
        "num_designs": 200,
        "diffuser_t": 50,
        "paper_info": {
            "target": "RSV-F Site I (7LVW)",
            "epitope": "site I",
            "citation": "Bennett et al., Table 5",
        },
    },
    {
        "name": "RSV_Site_III",
        "pdb": "rsv_site3.pdb",          # from RFantibody example_inputs (chain T, pre-processed)
        "framework": VHH_FRAMEWORK,
        "hotspots": "T305,T456",
        "design_loops": "H1:7,H2:6,H3:5-13",
        "num_designs": 200,
        "diffuser_t": 50,
        "paper_info": {
            "target": "RSV-F Site III (rsv_site3.pdb)",
            "epitope": "site III",
            "citation": "Bennett et al., Table 5",
        },
    },
    {
        "name": "Influenza_HA",
        "pdb": "flu_HA.pdb",              # from RFantibody example_inputs (chain B, pre-processed)
        "framework": VHH_FRAMEWORK,
        "hotspots": "B146,B170,B177",      # renumbered from 5VLI B521/B545/B552
        "design_loops": "H1:7,H2:6,H3:5-13",
        "num_designs": 200,
        "diffuser_t": 50,
        "paper_info": {
            "target": "Influenza HA (flu_HA.pdb)",
            "epitope": "stem",
            "citation": "Bennett et al., Table 5",
        },
    },
    {
        "name": "TcdB",
        "pdb": "6C0B.pdb",
        "framework": VHH_FRAMEWORK,
        "hotspots": "A1433,A1435,A1437,A1438,A1493",
        "design_loops": "H1:7,H2:6,H3:5-13",
        "num_designs": 200,
        "diffuser_t": 50,
        "paper_info": {
            "target": "TcdB (6C0B)",
            "epitope": "Frizzled interface",
            "citation": "Bennett et al., Table 5",
        },
    },
    {
        "name": "IL7R_alpha",
        "pdb": "3DI3.pdb",
        "framework": VHH_FRAMEWORK,
        "hotspots": "B81,B139,B192",
        "design_loops": "H1:7,H2:6,H3:5-13",
        "num_designs": 200,
        "diffuser_t": 50,
        "paper_info": {
            "target": "IL-7Rα (3DI3)",
            "epitope": "extracellular domain",
            "citation": "Bennett et al., Table 5",
        },
    },
]

# ---------------------------------------------------------------------------
# scFv design campaigns — Table 7 of the Supplementary Methods
# ---------------------------------------------------------------------------
SCFV_TARGETS = [
    {
        "name": "TcdB_scFv_unique",
        "pdb": "7ML7.pdb",
        "framework": SCFV_FRAMEWORK,
        "hotspots": "A1816,A1818,A1819,A1823,A1831",
        "design_loops": "H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13",
        "num_designs": 200,
        "diffuser_t": 50,
        "paper_info": {
            "target": "TcdB scFv unique pairing (7ML7)",
            "epitope": "CSPG4-binding site",
            "citation": "Bennett et al., Table 7",
        },
    },
    {
        "name": "TcdB_scFv_combinatorial",
        "pdb": "6C0B.pdb",
        "framework": SCFV_FRAMEWORK,
        "hotspots": "A1433,A1435,A1437,A1438,A1493",
        "design_loops": "H1:7,H2:6,H3:5-13,L1:7,L2:6,L3:5-13",
        "num_designs": 200,
        "diffuser_t": 50,
        "paper_info": {
            "target": "TcdB scFv combinatorial (6C0B)",
            "epitope": "Frizzled interface",
            "citation": "Bennett et al., Table 7",
        },
    },
]

# Combined list
TARGETS = VHH_TARGETS + SCFV_TARGETS

# --- ProteinMPNN step params (same for all targets) ---
MPNN_PARAMS = {
    "seqs_per_struct": 8,        # paper: 8 MPNN sequences per backbone
    "temperature": 0.2,
}

# --- RF2 filter params (same for all targets) ---
RF2_PARAMS = {
    "num_recycles": 10,          # paper: 10 recycles
}

# Ordered pipeline steps (same schema as before, but per-target now)
STEPS = [
    {
        "endpoint": "rfdiffusion",
        "consumes": None,          # uses target+framework uploads
        "produces": "1_rfdiffusion.qv",
    },
    {
        "endpoint": "proteinmpnn",
        "consumes": "1_rfdiffusion.qv",
        "produces": "2_proteinmpnn.qv",
    },
    {
        "endpoint": "rf2",
        "consumes": "2_proteinmpnn.qv",
        "produces": "3_rf2.qv",
    },
]

# In-silico acceptance filter — the RFantibody paper's minimal criteria
# ("Filtering Strategies" in the RFantibody README):
#     RF2 pAE < 10
#     RMSD (design vs RF2 predicted) < 2 Å
#
# The field names below MUST match the QV_SCORE keys emitted by the `rf2`
# endpoint (3_rf2.qv). They differ from the README/mock shorthand:
#     "RF2 pAE"                   -> `interaction_pae`  (a.k.a. pae_interaction)
#     "RMSD design vs RF2 pred."  -> `framework_aligned_cdr_rmsd`
# Other available keys: `pae` (overall), `pred_lddt`,
# `target_aligned_antibody_rmsd`, `target_aligned_cdr_rmsd`,
# `framework_aligned_antibody_rmsd`, `framework_aligned_{H1,H2,H3,L1,L2,L3}_rmsd`.
FILTER = {
    "field": "interaction_pae",
    "op": "<",
    "threshold": 10.0,
    "rmsd_field": "framework_aligned_cdr_rmsd",
    "rmsd_max": 2.0,              # self-consistency RMSD < 2 Å (paper criterion)
}