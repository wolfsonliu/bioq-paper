#!/usr/bin/env python3
"""Merge multiple RFdiffusion Quiver files into one, renumbering tags.

Usage:
    python3 merge_quivers.py results/HIV_Env/batch_*/rf2/3_rf2.qv \\
        -o results/HIV_Env/merged/3_rf2.qv
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def merge_quivers(input_paths: list[Path], output_path: Path,
                  tag_prefix: str = "design") -> int:
    """Merge multiple Quiver files, renumbering tags sequentially.

    Returns total number of designs.
    """
    tag_count = 0
    lines: list[str] = []

    for qv_path in input_paths:
        if not qv_path.exists():
            print(f"  WARNING: {qv_path} not found, skipping")
            continue
        text = qv_path.read_text()
        for line in text.splitlines():
            if line.startswith("QV_TAG "):
                # Rename: QV_TAG old_tag -> QV_TAG design_{tag_count:04d}
                new_tag = f"{tag_prefix}_{tag_count:04d}"
                lines.append(f"QV_TAG {new_tag}")
                tag_count += 1
            elif line.startswith("QV_SCORE "):
                # Rename: QV_SCORE old_tag rest -> QV_SCORE design_{tag_count-1:04d} rest
                parts = line.split(None, 2)
                old_tag = parts[1] if len(parts) > 1 else ""
                new_tag = f"{tag_prefix}_{tag_count - 1:04d}"
                rest = parts[2] if len(parts) > 2 else ""
                lines.append(f"QV_SCORE {new_tag} {rest}")
            else:
                lines.append(line)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n")
    print(f"merged {len(input_paths)} quivers -> {output_path} ({tag_count} designs)")
    return tag_count


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Merge RFdiffusion Quiver files from parallel batches")
    ap.add_argument("input_qvs", nargs="+", type=Path,
                    help="Quiver files to merge (glob patterns supported)")
    ap.add_argument("-o", "--output", type=Path, required=True,
                    help="Output merged Quiver path")
    ap.add_argument("--tag-prefix", default="design",
                    help="Tag prefix for renumbered designs (default: 'design')")
    args = ap.parse_args()

    # Expand glob patterns
    input_paths: list[Path] = []
    for p in args.input_qvs:
        if "*" in str(p) or "?" in str(p):
            expanded = sorted(Path().glob(str(p)))
            input_paths.extend(expanded)
            print(f"  glob {p} -> {len(expanded)} files")
        else:
            input_paths.append(p)

    if not input_paths:
        print("No input Quiver files found")
        return

    merge_quivers(input_paths, args.output, args.tag_prefix)


if __name__ == "__main__":
    main()