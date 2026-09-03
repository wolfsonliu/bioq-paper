#!/usr/bin/env python3
"""Collect per-service VRAM data (stdlib only, no cloud/GPU).

Sources, in priority order (see README "Data source"):
  1. curated overrides  — data/minima_curated.csv (author-maintained; authoritative
                          for `min_vram_gb`/`kind`/`source`/`confidence`)
  2. upstream README    — data/upstream_docs/<repo>/ (committed snapshot; falls back
                          to ./opensource/<repo>/) — grep for minimums and cards
  3. wrapper README     — bioq-services services/<svc>-server/README.md (secondary)
  4. FC provisioned GPU — bioq-services services/<svc>-server/deploy/fc*.yaml
                          (gpuConfig.gpuType + gpuConfig.gpuMemorySize, MB)

Writes data/vram.csv (one row per service):
  service, gpu_class, fc_vram_gb, min_vram_gb, kind, source, confidence

`kind` values: cpu | minimum | tested | unverified (curated may add `inferred`).
Only `kind == minimum` is a documented floor and feeds the figure's minimum
markers; `tested` is a documented *upper reference* (a card the authors used);
`unverified` means no statement was found. `cpu` services have no gpuConfig.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_BIOQ = HERE.parents[2] / "bioq-services"
DEFAULT_OPENSOURCE = HERE / "opensource"
DEFAULT_UPSTREAM_DOCS = HERE / "data" / "upstream_docs"
DEFAULT_MANIFEST = HERE.parent / "dependency_incompatibility" / "data" / "repo_manifest.csv"
DEFAULT_CURATED = HERE / "data" / "minima_curated.csv"
DEFAULT_OUT = HERE / "data" / "vram.csv"

FIELDS = ["service", "gpu_class", "fc_vram_gb", "min_vram_gb", "kind", "source", "confidence"]

# --- signal detection ---------------------------------------------------------
CARD_RE = re.compile(
    r"\b(?:A100|H100|H200|V100|P100|T4|A10|A30|A6000|L4|L40|B200|B100|"
    r"RTX\s*\d{3,4}|GTX\s*\d{3,4}|Titan|Quadro|Tesla|Ada|Ampere|Blackwell)\b",
    re.IGNORECASE,
)
GPU_CTX_RE = re.compile(r"gpu|vram|video\s*(?:ram|memory)|accelerator|cuda|显存", re.IGNORECASE)
# Lines that explicitly state GPU is *not* needed — skip, they are CPU specs.
NO_GPU_RE = re.compile(
    r"no\s+gpu|no\s+graphics|without\s+gp?u|cpu[-\s]?only|cpu\s+instance|"
    r"无需\s*GPU|不需要\s*GPU|无\s*GPU",
    re.IGNORECASE,
)
CAP_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[Gg](?:[Ii])?[Bb]")  # "16 GB"/"16 Gb"/"8 GiB"
# "minimum / sufficient" bound keywords: English plus the Chinese markers the
# bioq-services wrapper READMEs actually use ("8 GB 起步 / 即可 / 绰绰有余 / 足够").
MIN_KW_RE = re.compile(
    r"at\s+least|\bmin(?:imum)?\b|requir(?:es|e|ed)?\b|needs?\b|suffic(?:ient|es)?\b|>=|≥|"
    r"is\s+enough|\benough\b|"
    r"至少|最小|最低|起步|即可|绰绰有余|足够|可(?:跑|行|用)",
    re.IGNORECASE,
)

README_CANDIDATES = ["README.md", "readme.md", "README.rst", "README-zh.md"]


def truncate(s: str, n: int = 140) -> str:
    return s if len(s) <= n else s[: n - 3] + "..."


def load_repo_manifest(path: Path) -> dict[str, str]:
    """service(-server) -> upstream repo dir basename ('' if none)."""
    mapping: dict[str, str] = {}
    if not path.exists():
        return mapping
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            svc = (row.get("service") or "").strip()
            repo = (row.get("repo") or "").strip()
            if svc:
                mapping[svc] = Path(repo).name if repo else ""
    return mapping


def load_curated(path: Path) -> dict[str, dict[str, str]]:
    d: dict[str, dict[str, str]] = {}
    if not path or not path.exists():
        return d
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            svc = (row.get("service") or "").strip()
            if not svc:
                continue
            d[svc] = {
                "min_vram_gb": (row.get("min_vram_gb") or "").strip(),
                "kind": (row.get("kind") or "").strip(),
                "source": (row.get("source") or "").strip(),
                "confidence": (row.get("confidence") or "").strip(),
            }
    return d


def load_upstream_docs_index(path: Path) -> dict[str, list[str]]:
    """repo -> candidate README relpaths (from index.csv rows with reason==readme)."""
    d: dict[str, list[str]] = {}
    if not path.exists():
        return d
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("reason") or "").strip() != "readme":
                continue
            repo = (row.get("repo") or "").strip()
            rel = (row.get("relpath") or "").strip()
            if repo and rel and rel not in d.get(repo, []):
                d.setdefault(repo, []).append(rel)
    return d


def resolve_upstream_readme(
    repo: str, idx_relpaths: list[str], upstream_docs: Path, opensrc: Path
) -> tuple[Path | None, str]:
    """Find the upstream README, prefer the committed snapshot then the symlink."""
    cands = list(idx_relpaths) + [c for c in README_CANDIDATES if c not in idx_relpaths]
    for rel in cands:
        for root, tag in ((upstream_docs, "upstream_docs"), (opensrc, "opensource")):
            p = root / repo / rel
            if p.is_file():
                return p, f"{tag}/{repo}/{rel}"
    return None, ""


def list_services(bioq: Path) -> list[str]:
    d = bioq / "services"
    if not d.is_dir():
        return []
    return sorted(p.name for p in d.iterdir() if p.is_dir() and p.name.endswith("-server"))


def read_fc_gpu(bioq: Path, svc: str) -> tuple[str, str]:
    """(gpu_class, fc_vram_gb). Empty strings if no gpuConfig block found."""
    deploy = bioq / "services" / svc / "deploy"
    classes: set[str] = set()
    max_mb = 0
    found = False
    if deploy.is_dir():
        for y in sorted(list(deploy.glob("*.yaml")) + list(deploy.glob("*.yml"))):
            txt = y.read_text(errors="replace")
            if "gpuConfig:" not in txt:
                continue
            m_type = re.search(r"gpuType:\s*(\S+)", txt)
            m_mem = re.search(r"gpuMemorySize:\s*(\d+)", txt)
            if m_type:
                classes.add(m_type.group(1))
            if m_mem:
                found = True
                max_mb = max(max_mb, int(m_mem.group(1)))
    gpu_class = ",".join(sorted(classes))
    fc_gb = "" if not found else ("%g" % (max_mb / 1024.0))
    return gpu_class, fc_gb


def grep_readme_hints(targets: list[tuple[Path | None, str]]) -> tuple[str, str, str]:
    """Return (kind, min_vram_gb, source). kind in {minimum, tested, unverified}."""
    found_min: tuple[str, str] | None = None
    found_tested: tuple[str, str] | None = None
    for fp, label in targets:
        if not fp or not fp.is_file():
            continue
        for ln, raw in enumerate(fp.read_text(errors="replace").splitlines(), 1):
            line = raw.strip()
            if not line or not GPU_CTX_RE.search(line):
                continue
            if NO_GPU_RE.search(line):
                continue
            cap = CAP_RE.search(line)
            card = CARD_RE.search(line)
            if not cap and not card:
                continue
            src = f"{label}:{ln}: {truncate(line)}"
            if cap and MIN_KW_RE.search(line) and found_min is None:
                found_min = (cap.group(1), src)
            elif card and found_tested is None:
                found_tested = (card.group(0), src)
    if found_min:
        return "minimum", found_min[0], found_min[1]
    if found_tested:
        return "tested", "", found_tested[1]
    return "unverified", "", ""


def main() -> int:
    ap = argparse.ArgumentParser(description="Compute barrier: collect per-service VRAM data -> data/vram.csv")
    ap.add_argument("--bioq-services", default=str(DEFAULT_BIOQ))
    ap.add_argument("--opensource", default=str(DEFAULT_OPENSOURCE))
    ap.add_argument("--upstream-docs", default=str(DEFAULT_UPSTREAM_DOCS))
    ap.add_argument("--repo-manifest", default=str(DEFAULT_MANIFEST))
    ap.add_argument("--curated", default=str(DEFAULT_CURATED))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    bioq = Path(args.bioq_services)
    opensrc = Path(args.opensource)
    upstream_docs = Path(args.upstream_docs)
    services = list_services(bioq)
    if not services:
        print(f"ERROR: no *-server dirs under {bioq / 'services'}", file=sys.stderr)
        return 1

    mapping = load_repo_manifest(Path(args.repo_manifest))
    os_dirs = {d.name.lower(): d.name for d in opensrc.iterdir() if d.is_dir()} if opensrc.is_dir() else {}
    upstream_index = load_upstream_docs_index(upstream_docs / "index.csv")

    curated = load_curated(Path(args.curated))

    rows: list[dict[str, str]] = []
    stats: Counter[str] = Counter()

    for svc in services:
        gpu_class, fc_gb = read_fc_gpu(bioq, svc)
        name = svc[: -len("-server")]

        repo = mapping.get(svc)
        if repo is None:
            repo = os_dirs.get(name.lower(), "")

        upstream_readme: Path | None = None
        upstream_label = ""
        if repo:
            upstream_readme, upstream_label = resolve_upstream_readme(
                repo, upstream_index.get(repo, []), upstream_docs, opensrc
            )

        wrapper_readme = bioq / "services" / svc / "README.md"
        if not wrapper_readme.is_file():
            wrapper_readme = None  # type: ignore[assignment]

        targets: list[tuple[Path | None, str]] = []
        if upstream_readme is not None:
            targets.append((upstream_readme, upstream_label))
        if wrapper_readme is not None:
            targets.append((wrapper_readme, f"bioq-services/services/{svc}/README.md"))

        kind, min_v, source = grep_readme_hints(targets)

        # Curated overrides win (author-verified).
        if svc in curated:
            c = curated[svc]
            min_v = c["min_vram_gb"]
            kind = c["kind"] or kind
            source = c["source"] or source
            confidence = c["confidence"]
        elif kind == "minimum":
            confidence = "low"
        else:
            confidence = ""

        # A service with no gpuConfig and no GPU mention in its docs is CPU-only.
        if not gpu_class and not fc_gb and kind == "unverified":
            kind = "cpu"

        stats[kind] += 1
        rows.append({
            "service": svc,
            "gpu_class": gpu_class,
            "fc_vram_gb": fc_gb,
            "min_vram_gb": min_v,
            "kind": kind,
            "source": source,
            "confidence": confidence,
        })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    gpu_n = sum(1 for r in rows if r["fc_vram_gb"] != "")
    cpu_n = len(rows) - gpu_n
    print(f"services: {len(rows)}  (GPU-provisioned {gpu_n}, CPU/no-gpuConfig {cpu_n})")
    print(f"kind breakdown: {dict(sorted(stats.items()))}")
    print(f"wrote {out}")

    to_curate = [r["service"] for r in rows if r["kind"] in ("tested", "unverified") and r["fc_vram_gb"] != ""]
    if to_curate:
        print(f"\n{len(to_curate)} GPU services lack a documented minimum (curate in data/minima_curated.csv):")
        for svc in to_curate:
            print(f"  - {svc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())