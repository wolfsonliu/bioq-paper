#!/usr/bin/env python3
"""Fabricate mock Quiver outputs so analyze.py + plot.py can be exercised
WITHOUT the ECS stack. NOT real data — self-test / example figure only.
Writes results/<target>/{rfdiffusion,proteinmpnn,rf2}/*.qv.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import config as cfg

HERE = Path(__file__).resolve().parent
R = HERE / "results"

N_BACKBONES = 20
SEQS_PER = 4
N_DESIGNS = N_BACKBONES * SEQS_PER  # 80


def write_qv(path: Path, n: int, scored: bool, pass_rate_bias: float = 0.0) -> None:
    """Write a mock Quiver file. pass_rate_bias shifts the pae distribution."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for i in range(n):
        tag = f"design_{i:03d}"
        lines.append(f"QV_TAG {tag}")
        if scored:
            # Shift pae by pass_rate_bias (0 = ~1/3 pass, 1 = ~2/3 pass)
            offset = pass_rate_bias * 6.0
            pae = round(6.0 + 12.0 * (0.5 + 0.5 * math.sin(i)) - offset, 2)
            rmsd = round(0.8 + 1.6 * (0.5 + 0.5 * math.cos(i)), 2)
            # Emit the real RF2 score keys so analyze.py's FILTER matches mock
            # data the same way it matches server output.
            lines.append(f"QV_SCORE {tag} " + json.dumps(
                {"interaction_pae": pae,
                 "framework_aligned_cdr_rmsd": rmsd,
                 "pred_lddt": round(0.80 + 0.10 * math.sin(i), 2)}))
        lines.append(f"REMARK mock {tag}")
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    for i, tgt in enumerate(cfg.TARGETS):
        name = tgt["name"]
        bias = (i % 3) * 0.3  # vary pass rate across targets
        write_qv(R / name / "rfdiffusion" / "1_rfdiffusion.qv",
                 N_BACKBONES, False)
        write_qv(R / name / "proteinmpnn" / "2_proteinmpnn.qv",
                 N_DESIGNS, False)
        write_qv(R / name / "rf2" / "3_rf2.qv",
                 N_DESIGNS, True, bias)
        print(f"  {name}: mock quivers written (pass bias={bias:.1f})")
    print(f"\ndone. mock data under {R.relative_to(HERE)}/")


if __name__ == "__main__":
    main()