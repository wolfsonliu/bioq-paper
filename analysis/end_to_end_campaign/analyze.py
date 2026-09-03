#!/usr/bin/env python3
"""rfantibody — score the campaign into per-target funnel tables.  ***Offline.***

Streams the RF2 Quiver score records line-by-line (never loads a whole ``.qv``
into memory), so it scales to the full 9-target campaign — including the ~1.7 GB
merged RF2 quiver.  It is batch-aware and handles three on-disk layouts:

  1. parallel batches (what the server produced):
       results/<target>/batch_*/{rfdiffusion,proteinmpnn,rf2}/*.qv
  2. single run (historical layout):
       results/<target>/{rfdiffusion,proteinmpnn,rf2}/*.qv
  3. pre-merged RF2 (optional, from ``merge_quivers.py``):
       results/<target>/merged/3_rf2.qv   (takes precedence over batches)

Filter — the RFantibody paper's minimal in-silico criteria ("Filtering
Strategies" in the RFantibody README):

    RF2 interface pAE            < 10   (score field ``interaction_pae``)
    RMSD(design vs RF2 predicted) < 2 Å  (score field ``framework_aligned_cdr_rmsd``)

Usage:

    python3 analyze.py                       # every target found under results/
    python3 analyze.py --target HIV_Env      # one target
    python3 analyze.py --target HIV_Env,RSV_Site_I
    python3 analyze.py --from-data           # recompute funnels from data/<target>/designs.csv

Outputs:

    data/<target>/designs.csv    per-design score table (one row per RF2 score)
    data/<target>/funnel.json    per-target funnel (stages + pass fractions)
    data/<target>/funnel.csv     2-column stage/count CSV
    data/campaign_summary.json   all funnels
    data/campaign_summary.csv    one row per target
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
from pathlib import Path

import config as cfg

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DATA = HERE / "data"

# stage dir -> produced quiver filename (matches config.STEPS)
STAGE_FILES = {
    "rfdiffusion": "1_rfdiffusion.qv",
    "proteinmpnn": "2_proteinmpnn.qv",
    "rf2": "3_rf2.qv",
}


# ---------------------------------------------------------------------------
# Quiver parsing (streaming)
# ---------------------------------------------------------------------------

def _to_number(value):
    """Coerce to finite float when possible; else return the raw value.

    NaN strings are kept as strings so they are NOT treated as numeric scores
    (and thus never counted as "scored" or matched by a threshold).
    """
    if isinstance(value, bool):
        return value
    try:
        v = float(value)
    except (TypeError, ValueError):
        return value
    if math.isnan(v) or math.isinf(v):
        return value
    return v


def _parse_score_blob(blob: str) -> dict:
    """Parse a QV_SCORE payload: either JSON (mock) or ``k=v|k=v`` (real RF2)."""
    blob = blob.strip()
    if not blob:
        return {}
    if blob.startswith("{"):
        try:
            raw = json.loads(blob)
        except json.JSONDecodeError:
            raw = None
        if isinstance(raw, dict):
            return {k: _to_number(v) for k, v in raw.items()}
    out: dict = {}
    for tok in re.split(r"[\s|,]+", blob):
        if "=" not in tok and ":" not in tok:
            continue
        k, v = re.split(r"[=:]", tok, maxsplit=1)
        k = k.strip()
        if k:
            out[k] = _to_number(v.strip())
    return out


def iter_quiver(paths):
    """Yield ``(kind, tag, rest)`` for QV_TAG / QV_SCORE lines, across many files.

    ``kind`` is ``"tag"`` or ``"score"``.  PDB/ATOM/REMARK payload lines are
    skipped.  Files are streamed, so total memory stays flat regardless of size.
    """
    for path in paths:
        with path.open(errors="replace") as fh:
            for line in fh:
                if line.startswith("QV_TAG "):
                    yield "tag", line[len("QV_TAG "):].strip(), ""
                elif line.startswith("QV_SCORE "):
                    parts = line.split(None, 2)
                    tag = parts[1] if len(parts) > 1 else ""
                    rest = parts[2] if len(parts) > 2 else ""
                    yield "score", tag, rest


def count_tags(paths) -> int:
    return sum(1 for kind, *_ in iter_quiver(paths) if kind == "tag")


def load_scores(paths) -> list[dict]:
    """Extract per-design score dicts from QV_SCORE lines (streaming)."""
    rows: list[dict] = []
    for kind, tag, rest in iter_quiver(paths):
        if kind == "score":
            rows.append({"tag": tag, **_parse_score_blob(rest)})
    return rows


# ---------------------------------------------------------------------------
# Layout / path resolution
# ---------------------------------------------------------------------------

def stage_qvs(target_dir: Path, stage: str) -> list[Path]:
    """Resolve the *.<stage>.qv files for a target, covering batch + flat layouts."""
    fname = STAGE_FILES[stage]
    paths = sorted(target_dir.glob(f"batch_*/{stage}/{fname}"))
    flat = target_dir / stage / fname
    if flat.exists() and flat not in paths:
        paths.append(flat)
    return paths


def rf2_qvs(target_dir: Path) -> list[Path]:
    """RF2 quivers to score.  A merged quiver supersedes the per-batch files."""
    merged = target_dir / "merged" / STAGE_FILES["rf2"]
    if merged.exists():
        return [merged]
    return stage_qvs(target_dir, "rf2")


# ---------------------------------------------------------------------------
# Filter / funnel
# ---------------------------------------------------------------------------

def _pae_pass(value, f: dict) -> bool:
    field, thr, op = f["field"], f["threshold"], f["op"]
    if not isinstance(value, (int, float)):
        return False
    if op == "<":
        return value < thr
    if op == ">":
        return value > thr
    return value == thr


def _filter_pass(d: dict, f: dict) -> bool:
    if not _pae_pass(d.get(f["field"]), f):
        return False
    rmsd_field = f.get("rmsd_field")
    if rmsd_field and f.get("rmsd_max") is not None:
        r = d.get(rmsd_field)
        return isinstance(r, (int, float)) and r < f["rmsd_max"]
    return True


def _filter_desc(f: dict) -> str:
    s = f"{f['field']} {f['op']} {f['threshold']}"
    if f.get("rmsd_max") is not None and f.get("rmsd_field"):
        s += f" & {f['rmsd_field']} < {f['rmsd_max']}"
    return s


def _backbone_pass(designs: list[dict]) -> dict:
    """Best-of-8 backbone success, in the paper's convention.

    MPNN emits ``seqs_per_struct`` sequences per backbone **in order**, so runs
    of ``seqs_per_struct`` consecutive score records share one backbone.  A
    backbone is a *success* if its best-by-filter sequence (lowest
    ``interaction_pae``) passes the full filter — matching the RFantibody paper
    ("the best of 8 MPNN sequences ... were used to determine success rates"),
    whose success rate is per-backbone, not per-sequence.
    """
    f = cfg.FILTER
    seqs = cfg.MPNN_PARAMS.get("seqs_per_struct", 8)
    field = f["field"]
    n_groups = 0
    n_pass = 0
    for i in range(0, len(designs), seqs):
        group = designs[i:i + seqs]
        best = None
        for d in group:
            v = d.get(field)
            if isinstance(v, (int, float)):
                bv = best.get(field) if best is not None else None
                if bv is None or not isinstance(bv, (int, float)) or v < bv:
                    best = d
        if best is not None:
            n_groups += 1
            if _filter_pass(best, f):
                n_pass += 1
    return {
        "backbones_scored": n_groups,
        "backbone_pass": n_pass,
        "backbone_pass_fraction": round(n_pass / n_groups, 4) if n_groups else None,
    }


def build_funnel(target_name: str, designs: list[dict],
                 n_backbones: int | None, n_seqs: int | None,
                 sources: list[Path]) -> dict:
    f = cfg.FILTER
    field = f["field"]
    scored = [d for d in designs if isinstance(d.get(field), (int, float))]
    n_scored = len(scored)
    n_pae = sum(1 for d in scored if _pae_pass(d.get(field), f))
    n_pass = sum(1 for d in scored if _filter_pass(d, f))

    pae_frac = round(n_pae / n_scored, 4) if n_scored else None
    pass_frac = round(n_pass / n_scored, 4) if n_scored else None
    bb = _backbone_pass(designs)

    return {
        "target": target_name,
        "filter": _filter_desc(f),
        "stages": {
            "rfdiffusion_backbones": n_backbones,
            "mpnn_sequences": n_seqs,
            "rf2_scored": n_scored,
            "pae_pass": n_pae,
            "passed_filter": n_pass,
        },
        "in_silico_pass_fraction": pass_frac,
        "pae_pass_fraction": pae_frac,
        "n_designs": n_scored,
        "backbones_scored": bb["backbones_scored"],
        "backbone_pass": bb["backbone_pass"],
        "backbone_pass_fraction": bb["backbone_pass_fraction"],
        "source": [str(s) for s in sources],
    }


# ---------------------------------------------------------------------------
# Per-target analysis
# ---------------------------------------------------------------------------

def analyze_target(target_name: str) -> dict | None:
    """Analyze one target under results/.  Returns a funnel dict, or None."""
    target_dir = RESULTS / target_name
    if not target_dir.exists():
        return None

    rf2_paths = rf2_qvs(target_dir)
    if not rf2_paths:
        return {"target": target_name, "status": "NOT_RUN",
                "note": f"no {STAGE_FILES['rf2']} found under results/{target_name}"}

    designs = load_scores(rf2_paths)
    n_backbones = count_tags(stage_qvs(target_dir, "rfdiffusion")) or None
    n_seqs = count_tags(stage_qvs(target_dir, "proteinmpnn")) or None

    if not designs:
        return {"target": target_name, "status": "EMPTY",
                "note": "RF2 quiver present but no QV_SCORE records found"}

    tgt_data = DATA / target_name
    tgt_data.mkdir(parents=True, exist_ok=True)

    # Per-design table: tag + every score key seen, sorted for a stable header.
    fields = ["tag"] + sorted({k for d in designs for k in d if k != "tag"})
    with (tgt_data / "designs.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(designs)

    funnel = build_funnel(target_name, designs, n_backbones, n_seqs, rf2_paths)
    (tgt_data / "funnel.json").write_text(json.dumps(funnel, indent=2))

    with (tgt_data / "funnel.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stage", "count"])
        for k, v in funnel["stages"].items():
            w.writerow([k, v])
        w.writerow(["pae_pass_fraction", funnel["pae_pass_fraction"]])
        w.writerow(["in_silico_pass_fraction", funnel["in_silico_pass_fraction"]])
        w.writerow(["backbone_pass", funnel["backbone_pass"]])
        w.writerow(["backbone_pass_fraction", funnel["backbone_pass_fraction"]])

    print(f"  {target_name}: {len(designs)} designs, "
          f"pae_pass={funnel['pae_pass_fraction']}, "
          f"pass={funnel['in_silico_pass_fraction']}, "
          f"backbone_pass={funnel['backbone_pass_fraction']}")
    return funnel


def load_designs_csv(path: Path) -> list[dict]:
    """Read data/<target>/designs.csv and coerce score values back to numbers.

    CSV round-trips every cell as a string, so ``_to_number`` restores the
    int/float types that ``build_funnel``'s filter matching relies on.
    """
    rows: list[dict] = []
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            rows.append({k: _to_number(v) for k, v in row.items()})
    return rows


def analyze_target_from_data(target_name: str) -> dict | None:
    """Recompute a target's funnel from ``data/<target>/designs.csv``.

    Used when the raw ``results/`` quivers are not present locally (only the
    exported ``data/`` tables were copied back).  ``designs.csv`` already holds
    the full per-design RF2 scores, so the funnel can be rebuilt with the
    current ``cfg.FILTER`` (which also repairs funnels computed earlier with an
    outdated field name, e.g. ``pae_interaction`` -> ``interaction_pae``).
    """
    csv_path = DATA / target_name / "designs.csv"
    if not csv_path.exists():
        return None
    designs = load_designs_csv(csv_path)
    if not designs:
        return {"target": target_name, "status": "EMPTY",
                "note": f"{csv_path} has no rows"}

    seqs = cfg.MPNN_PARAMS.get("seqs_per_struct", 8)
    n_backbones = (len(designs) + seqs - 1) // seqs
    n_seqs = len(designs)
    # Prefer the (already correct) designed counts from any prior funnel.json;
    # otherwise fall back to the counts derived from designs.csv.
    prior = DATA / target_name / "funnel.json"
    if prior.exists():
        try:
            stages = json.loads(prior.read_text()).get("stages", {})
            if isinstance(stages.get("rfdiffusion_backbones"), (int, float)):
                n_backbones = int(stages["rfdiffusion_backbones"])
            if isinstance(stages.get("mpnn_sequences"), (int, float)):
                n_seqs = int(stages["mpnn_sequences"])
        except (json.JSONDecodeError, OSError):
            pass

    funnel = build_funnel(target_name, designs, n_backbones, n_seqs, [csv_path])
    (DATA / target_name / "funnel.json").write_text(json.dumps(funnel, indent=2))

    with (DATA / target_name / "funnel.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stage", "count"])
        for k, v in funnel["stages"].items():
            w.writerow([k, v])
        w.writerow(["pae_pass_fraction", funnel["pae_pass_fraction"]])
        w.writerow(["in_silico_pass_fraction", funnel["in_silico_pass_fraction"]])
        w.writerow(["backbone_pass", funnel["backbone_pass"]])
        w.writerow(["backbone_pass_fraction", funnel["backbone_pass_fraction"]])

    print(f"  {target_name}: {len(designs)} designs, "
          f"pae_pass={funnel['pae_pass_fraction']}, "
          f"pass={funnel['in_silico_pass_fraction']}, "
          f"backbone_pass={funnel['backbone_pass_fraction']}")
    return funnel


# ---------------------------------------------------------------------------
# Campaign summary
# ---------------------------------------------------------------------------

def discover_targets() -> list[str]:
    """Every directory under results/ that contains any 3_rf2.qv recursively."""
    names = set()
    for d in RESULTS.iterdir():
        if d.is_dir() and any(d.glob(f"**/{STAGE_FILES['rf2']}")):
            names.add(d.name)
    return sorted(names)


def discover_data_targets() -> list[str]:
    """Every directory under data/ that contains a designs.csv."""
    names = set()
    for d in DATA.iterdir():
        if d.is_dir() and (d / "designs.csv").exists():
            names.add(d.name)
    return sorted(names)


def main() -> None:
    # Module-level RESULTS/DATA are rebound from CLI flags before analysis.
    global RESULTS, DATA

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--target", "--targets",
                    help="comma-separated target directory names (default: auto-detect)")
    ap.add_argument("--results", default=str(RESULTS), help="results root")
    ap.add_argument("--data", default=str(DATA), help="data output root")
    ap.add_argument("--from-data", action="store_true",
                    help="recompute funnels from data/<target>/designs.csv "
                         "(offline; no results/ quivers needed)")
    args = ap.parse_args()

    RESULTS = Path(args.results)
    DATA = Path(args.data)
    from_data = args.from_data

    env = os.environ.get("E5_TARGET", "")
    if args.target:
        target_names = [x.strip() for x in args.target.split(",") if x.strip()]
    elif env:
        target_names = [x.strip() for x in env.split(",") if x.strip()]
    else:
        target_names = discover_data_targets() if from_data else discover_targets()

    if not target_names:
        where = "data/" if from_data else "results/"
        print(f"No targets found under {where}. Run the campaign first "
              "(or pass --target).")
        sys.exit(1)

    DATA.mkdir(parents=True, exist_ok=True)
    analyze = analyze_target_from_data if from_data else analyze_target
    src_root = DATA if from_data else RESULTS
    all_funnels = []
    print(f"Analyzing {len(target_names)} target(s) from {src_root}:")
    for name in target_names:
        funnel = analyze(name)
        if funnel and funnel.get("status") is None:
            all_funnels.append(funnel)
        elif funnel:
            print(f"  {name}: {funnel.get('status')} — {funnel.get('note','')}")

    if all_funnels:
        (DATA / "campaign_summary.json").write_text(
            json.dumps(all_funnels, indent=2))

        with (DATA / "campaign_summary.csv").open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["target", "backbones", "mpnn_seqs", "rf2_scored",
                        "pae_pass", "pae_pass_fraction",
                        "passed_filter", "in_silico_pass_fraction",
                        "backbone_pass", "backbone_pass_fraction"])
            for f in all_funnels:
                s = f.get("stages", {})
                w.writerow([
                    f["target"],
                    s.get("rfdiffusion_backbones", ""),
                    s.get("mpnn_sequences", ""),
                    s.get("rf2_scored", ""),
                    s.get("pae_pass", ""),
                    f.get("pae_pass_fraction", ""),
                    s.get("passed_filter", ""),
                    f.get("in_silico_pass_fraction", ""),
                    f.get("backbone_pass", ""),
                    f.get("backbone_pass_fraction", ""),
                ])

        print(f"\nCampaign summary: {len(all_funnels)} target(s) analyzed")
        print(f"  {DATA / 'campaign_summary.csv'}")
        print(f"  {DATA / 'campaign_summary.json'}")
    else:
        print("No scorable targets found (no RF2 QV_SCORE records).")


if __name__ == "__main__":
    main()