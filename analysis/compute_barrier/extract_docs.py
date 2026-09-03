#!/usr/bin/env python3
"""Extract resource-requirement documentation from upstream checkouts into
`data/upstream_docs/<repo>/` for the compute-barrier / VRAM audit.

For every project under `opensource/`, this copies the README plus any other
documentation file that mentions hardware/resource requirements (GPU / VRAM /
CUDA / data-center card classes / memory footprint / disk space) into a
committed, verbatim evidence corpus, so every `min_vram_gb` value in the compute-barrier audit is
auditable against its source without depending on the `opensource/` symlink or
an absolute path.

Scope per repo (deliberately narrow, to avoid vendored sub-repo noise):
  * repo root — README* and install/setup/requirement/hardware/usage-style files
  * repo `docs/` subtree — any text file that matches a resource signal

Outputs:
  data/upstream_docs/<repo>/<relpath>   — the copied documentation files
  data/upstream_docs/index.csv          — one row per copied file
  data/upstream_docs/hits.tsv           — matched lines (for quote extraction)

Stdlib only. Safe to re-run (clears and rewrites the output dir).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import sys
from pathlib import Path

# --- Configuration -----------------------------------------------------------

# Basenames (stem, lowercased) that are always copied from the repo root, even
# without a resource match.
ALWAYS_COPY_STEMS = {
    "readme",
    "install",
    "installation",
    "installing",
    "setup",
    "requirements",
    "requirement",
    "hardware",
    "quickstart",
    "quick-start",
    "quick_start",
    "getting-started",
    "getting_started",
    "usage",
    "running",
}

TEXT_EXTS = {".md", ".rst", ".txt", ".markdown", ".adoc", ".org"}

# Vendored / noise directories we never descend into (they duplicate the
# upstream tool's own READMEs, e.g. RFdiffusion's env/SE3Transformer).
SKIP_DIRS = {
    ".git",
    ".github",
    ".circleci",
    "__pycache__",
    "node_modules",
    "env",
    "include",
    "lib",
    "rf2aa",
    "tool",
    "tools",
}

# Resource-requirement signals, grouped so the index reports *why* a file was
# included. Kept deliberately specific to avoid matching every "GB" file size.
RESOURCE_PATTERNS: dict[str, str] = {
    "vram": r"\bvram\b",
    "gpu_memory": r"\bgpu\s*memory\b",
    "video_memory": r"\bvideo\s*memory\b",
    "datacenter_gpu": r"\b(a100|h100|h200|v100|a10|a30)\b",
    "consumer_gpu": r"\brtx\s?[0-9]{4}\b|\b(gtx|quadro|titan)\b",
    "nvidia": r"\bnvidia\b",
    "cuda": r"\bcuda\b",
    "requires_gpu": r"requires?\s+(a\s+|an\s+)?gpu",
    "gpu_requirement": r"gpu[- ]?(require|recommend|accelerat|support|needed)",
    "min_memory": r"(?:at least|minimum(?:\s+of)?)\s+\d+\s*(?:gb|gib|tb)"
    r"|\d+\s*(?:gb|gib)\s+(?:of\s+)?(?:gpu|video|vram)",
    "memory_footprint": r"memory[- ]?(footprint|requirement|usage)",
    "disk": r"disk\s+space|free\s+disk|\btb\b\s+(?:of\s+)?(?:disk|storage)",
}

MAX_FILE_BYTES = 2 * 1024 * 1024  # skip gigantic text files

_COMPILED = {name: re.compile(p, re.IGNORECASE) for name, p in RESOURCE_PATTERNS.items()}


def is_text_file(path: Path) -> bool:
    try:
        head = path.read_bytes()[:8192]
    except OSError:
        return False
    return b"\x00" not in head


def matched_patterns(text: str) -> list[str]:
    return [name for name, rx in _COMPILED.items() if rx.search(text)]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_repo_files(repo: Path) -> list[tuple[Path, str]]:
    """Return [(abs_path, relpath)] of candidate documentation files."""
    out: list[tuple[Path, str]] = []

    # (1) repo root, depth 1.
    for f in sorted(repo.iterdir()):
        if not f.is_file() or f.is_symlink():
            continue
        stem = f.name.rsplit(".", 1)[0].lower()
        if f.suffix.lower() in TEXT_EXTS and (stem in ALWAYS_COPY_STEMS or stem.startswith("readme")):
            out.append((f, f.name))

    # (2) docs/ subtree.
    docs = repo / "docs"
    if docs.is_dir():
        for f in sorted(docs.rglob("*")):
            if not f.is_file() or f.is_symlink():
                continue
            rel = f.relative_to(repo)
            if any(part in SKIP_DIRS for part in rel.parts):
                continue
            if f.suffix.lower() not in TEXT_EXTS:
                continue
            out.append((f, rel.as_posix()))

    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument(
        "--opensource",
        default=str(here / "opensource"),
        help="upstream checkout dir (default: ./opensource next to this script)",
    )
    parser.add_argument(
        "--out",
        default=str(here / "data" / "upstream_docs"),
        help="output corpus dir (default: data/upstream_docs)",
    )
    parser.add_argument("--dry-run", action="store_true", help="print plan, copy nothing")
    args = parser.parse_args(argv)

    opensource = Path(args.opensource).resolve()
    if not opensource.is_dir():
        print(f"error: --opensource not a directory: {opensource}", file=sys.stderr)
        return 2

    out_dir = Path(args.out)
    if not args.dry_run:
        if out_dir.exists():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

    repos = sorted(
        d for d in opensource.iterdir() if d.is_dir() and d.name not in SKIP_DIRS
    )

    index_rows: list[dict] = []
    hit_rows: list[dict] = []
    total_bytes = 0
    skipped_big = 0

    for repo in repos:
        for src, rel in collect_repo_files(repo):
            try:
                size = src.stat().st_size
            except OSError:
                continue
            if size > MAX_FILE_BYTES:
                skipped_big += 1
                continue
            if not is_text_file(src):
                continue

            try:
                text = src.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            pats = matched_patterns(text)
            is_readme = rel.lower().startswith("readme")
            include = is_readme or bool(pats)

            if not include:
                continue

            dst = out_dir / repo.name / rel
            if not args.dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

            total_bytes += size
            index_rows.append(
                {
                    "repo": repo.name,
                    "relpath": rel,
                    "reason": "readme" if is_readme else "content",
                    "matched_patterns": ",".join(pats),
                    "size_bytes": size,
                    "sha256": sha256(src),
                    "source": str(src),
                }
            )

            # matched lines (for later quote extraction by collect_vram.py)
            for lineno, line in enumerate(text.splitlines(), 1):
                lp = matched_patterns(line)
                if lp:
                    hit_rows.append(
                        {
                            "repo": repo.name,
                            "relpath": rel,
                            "line": lineno,
                            "matched_patterns": ",".join(lp),
                            "text": line.strip(),
                        }
                    )

    if not args.dry_run:
        with (out_dir / "index.csv").open("w", newline="") as fh:
            w = csv.DictWriter(
                fh,
                fieldnames=[
                    "repo",
                    "relpath",
                    "reason",
                    "matched_patterns",
                    "size_bytes",
                    "sha256",
                    "source",
                ],
            )
            w.writeheader()
            w.writerows(index_rows)

        with (out_dir / "hits.tsv").open("w", newline="") as fh:
            w = csv.DictWriter(
                fh,
                fieldnames=["repo", "relpath", "line", "matched_patterns", "text"],
                dialect="excel-tab",
            )
            w.writeheader()
            w.writerows(hit_rows)

    n_repos_with_files = len({r["repo"] for r in index_rows})
    print(f"repos scanned: {len(repos)}")
    print(f"repos with copied docs: {n_repos_with_files}")
    print(f"files copied: {len(index_rows)}")
    print(f"matched lines: {len(hit_rows)}")
    print(f"total bytes: {total_bytes} ({total_bytes / 1_000_000:.2f} MB)")
    if skipped_big:
        print(f"skipped oversized files: {skipped_big}")
    if args.dry_run:
        print("dry-run: nothing written")
    else:
        print(f"output: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())