#!/usr/bin/env python3
"""Contract-conformance scoring: per-service conformance scores, fleet summary, and straggler tables.

Reads the checklist rows produced by audit.py (data/conformance.csv +
data/fleet.csv) and reduces them to the numbers reported in the paper:

  * endpoint score  = fraction of the 5 checklist items passed
  * service score   = mean endpoint score (task endpoints; all endpoints as
                      sensitivity column)
  * fleet summary   = % fully-conformant endpoints, % services >= threshold,
                      per-check pass rates, median service score
  * stragglers      = every endpoint missing >= 1 checklist item, with the
                      exact missing items (actionable contract fixes), plus
                      services not audited (no manifest at audit time —
                      excluded from all statistics, listed for transparency)

Outputs (under --data-dir):
  scores.csv       one row per service
  summary.json     fleet-level headline numbers
  stragglers.csv   non-conforming endpoints + missing items
  stragglers.md    the same, as a paste-ready markdown table

Usage:
    python3 score.py
    python3 score.py --threshold 0.9 --data-dir path/to/data

Requires only the Python stdlib.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from statistics import mean, median

CHECKS = ["typed_params", "file_fields", "defaults", "machine_view", "docs_text"]

SCORE_COLUMNS = [
    "service", "status", "version", "n_endpoints", "n_task_endpoints",
    "score_task", "score_all", "pct_full_task", "pct_full_all",
    "above_threshold",
]


def load_rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--threshold", type=float, default=0.9,
                    help="service-level conformance bar (default 0.9)")
    ap.add_argument("--data-dir", default=str(Path(__file__).parent / "data"))
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    conf = load_rows(data_dir / "conformance.csv")
    fleet = {r["service"]: r for r in load_rows(data_dir / "fleet.csv")}
    if not conf:
        print("error: conformance.csv is empty — run audit.py first", file=sys.stderr)
        return 1
    for r in conf:
        r["score"] = float(r["score"])
        r["is_task"] = int(r["is_task"])

    # ---- per-service scores ------------------------------------------------
    by_svc: dict[str, list[dict]] = {}
    for r in conf:
        by_svc.setdefault(r["service"], []).append(r)

    score_rows = []
    for svc, rows in sorted(by_svc.items()):
        task = [r for r in rows if r["is_task"]] or rows  # fallback: legacy-only svc
        score_task = mean(r["score"] for r in task)
        score_all = mean(r["score"] for r in rows)
        score_rows.append({
            "service": svc,
            "status": "audited",
            "version": fleet.get(svc, {}).get("version", ""),
            "n_endpoints": len(rows),
            "n_task_endpoints": sum(r["is_task"] for r in rows),
            "score_task": round(score_task, 4),
            "score_all": round(score_all, 4),
            "pct_full_task": round(100 * sum(r["score"] == 1.0 for r in task) / len(task), 1),
            "pct_full_all": round(100 * sum(r["score"] == 1.0 for r in rows) / len(rows), 1),
            "above_threshold": int(score_task >= args.threshold),
        })

    # Services whose manifest could not be fetched (cold start / unavailable at
    # audit time) are NOT scored: availability is an operational concern,
    # not a contract-conformance data point. They are listed as "unaudited" and
    # excluded from every fleet statistic below.
    unaudited = []
    for svc, fr in sorted(fleet.items()):
        if fr["manifest_ok"] == "0" and svc not in by_svc:
            unaudited.append({"service": svc,
                              "reason": fr.get("error", "") or "manifest fetch failed"})
            score_rows.append({
                "service": svc, "status": "unaudited", "version": "",
                "n_endpoints": 0, "n_task_endpoints": 0,
                "score_task": "", "score_all": "",
                "pct_full_task": "", "pct_full_all": "", "above_threshold": "",
            })
    audited = [r for r in score_rows if r["status"] == "audited"]
    score_rows.sort(key=lambda r: (r["status"] != "audited",
                                   -(r["score_task"] or 0), r["service"]))

    # ---- fleet summary -------------------------------------------------------
    task_rows = [r for r in conf if r["is_task"]] or conf
    n_svc_ok = sum(1 for fr in fleet.values() if fr["manifest_ok"] == "1")
    per_check = {
        c: {
            "pass_rate_task": round(sum(r[c] == "1" for r in task_rows) / len(task_rows), 4),
            "pass_rate_all": round(sum(r[c] == "1" for r in conf) / len(conf), 4),
        }
        for c in CHECKS
    }
    summary = {
        "n_services_listed": len(fleet),
        "n_services_audited": len(audited),
        "n_services_unaudited": len(unaudited),
        "unaudited": unaudited,
        "n_endpoints_all": len(conf),
        "n_endpoints_task": sum(r["is_task"] for r in conf),
        "pct_endpoints_fully_conformant_task": round(
            100 * sum(r["score"] == 1.0 for r in task_rows) / len(task_rows), 1),
        "pct_endpoints_fully_conformant_all": round(
            100 * sum(r["score"] == 1.0 for r in conf) / len(conf), 1),
        "threshold": args.threshold,
        "pct_services_above_threshold": round(
            100 * sum(r["above_threshold"] for r in audited) / len(audited), 1),
        "median_service_score_task": round(
            median(r["score_task"] for r in audited), 4),
        "mean_service_score_task": round(
            mean(r["score_task"] for r in audited), 4),
        "per_check": per_check,
    }

    # ---- stragglers ----------------------------------------------------------
    strag_rows = []
    for r in sorted(conf, key=lambda r: (r["score"], r["service"], r["endpoint"])):
        missing = [c for c in CHECKS if r[c] == "0"]
        if missing:
            strag_rows.append({
                "service": r["service"], "endpoint": r["endpoint"],
                "is_task": r["is_task"], "score": r["score"],
                "missing": "+".join(missing),
            })
    unreachable = [(u["service"], u["reason"]) for u in unaudited]

    # ---- write outputs -------------------------------------------------------
    with (data_dir / "scores.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=SCORE_COLUMNS)
        w.writeheader()
        w.writerows(score_rows)
    (data_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (data_dir / "stragglers.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["service", "endpoint", "is_task", "score", "missing"])
        w.writeheader()
        w.writerows(strag_rows)

    md = ["# Contract-conformance stragglers", ""]
    if unreachable:
        md += ["## Services not audited (no manifest at audit time)", "",
               "Excluded from all conformance statistics — availability is an",
               "operational axis, not a contract-conformance finding.", "",
               "| service | problem |", "|---|---|"]
        md += [f"| {s} | {err} |" for s, err in unreachable]
        md.append("")
    md += ["## Non-fully-conforming endpoints", "",
           "| service | endpoint | task | score | missing checks |",
           "|---|---|---|---|---|"]
    md += [f"| {r['service']} | `{r['endpoint']}` | {r['is_task']} | {r['score']:.1f} "
           f"| {r['missing']} |" for r in strag_rows]
    (data_dir / "stragglers.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # ---- console report ------------------------------------------------------
    print(f"fleet: {summary['n_services_audited']} audited / "
          f"{summary['n_services_unaudited']} unaudited of "
          f"{summary['n_services_listed']} listed | "
          f"{summary['n_endpoints_task']} task endpoints "
          f"({summary['n_endpoints_all']} total)")
    print(f"fully conformant endpoints: "
          f"{summary['pct_endpoints_fully_conformant_task']}% (task) / "
          f"{summary['pct_endpoints_fully_conformant_all']}% (all)")
    print(f"audited services >= {args.threshold}: "
          f"{summary['pct_services_above_threshold']}% | median service score "
          f"{summary['median_service_score_task']}")
    print("per-check pass rate (task endpoints):")
    for c in CHECKS:
        print(f"  {c:<14} {per_check[c]['pass_rate_task'] * 100:6.1f}%")
    print(f"stragglers: {len(strag_rows)} endpoints"
          + (f"; not audited: {', '.join(s for s, _ in unreachable)}"
             if unreachable else ""))
    print(f"wrote scores.csv, summary.json, stragglers.csv, stragglers.md in {data_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
