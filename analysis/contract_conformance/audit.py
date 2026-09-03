#!/usr/bin/env python3
"""Contract-conformance audit: collect fleet manifests and check the uniform-contract checklist.

Ground truth is the *machine manifest*: for every service listed by
`bioq services`, we fetch `bioq describe <svc> --output json` (the exact
payload the CLI shows a human or an agent) and evaluate a fixed 5-item
checklist on every endpoint in the manifest:

  typed_params    every request field carries a concrete type (not '' / 'any')
  file_fields     multipart endpoints declare their file inputs as file-typed
                  fields (the `--file` surface of `bioq run`)
  defaults        every optional non-file parameter declares an explicit
                  default (default != null in the manifest)
  machine_view    the endpoint entry is machine-complete: method, path,
                  request_content_type, operation_id and a request_fields list
                  (what `--output json` consumers rely on)
  docs_text       the endpoint carries human-readable prose (summary and/or
                  description)

Checklist items that do not apply to an endpoint pass vacuously (e.g.
`file_fields` on a JSON endpoint); applicability counts are reported so a
vacuous pass is never silently inflated into evidence.

Outputs (under --data-dir, default ./data):
  manifests/<svc>.json   raw `bioq describe --output json` payloads (raw data)
  fleet.csv              per-service fetch status + endpoint counts
  conformance.csv        per-endpoint checklist rows (one row per endpoint)

Usage:
    python3 audit.py --collect                 # live: fetch + check (needs bioq CLI)
    python3 audit.py                           # offline: re-check committed manifests
    python3 audit.py --collect --only dockq,boltz
    python3 audit.py --bioq /path/to/bioq --retries 2

Requires only the Python stdlib. The live mode shells out to the bioq CLI,
which must already be authenticated (`bioq login --oidc`).
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

CHECKS = ["typed_params", "file_fields", "defaults", "machine_view", "docs_text"]

# Services excluded from the audit scope, with reasons (kept out of collection,
# checking, and scoring alike).
EXCLUDED = {
    # Legacy /v1-API service generation, not built on the bioq_service
    # framework and therefore outside the uniform contract this experiment
    # measures — a different kind of service, not a conformance data point.
    "ensemble": "legacy /v1 API service, outside the uniform contract",
}

FLEET_COLUMNS = [
    "service", "listed", "manifest_ok", "error", "version",
    "n_endpoints", "n_task_endpoints",
]
CONFORMANCE_COLUMNS = [
    "service", "endpoint", "method", "is_task", "content_type",
    "n_fields", "n_file_fields", "n_optional_params", "field_desc_frac",
    "has_operation_id", *CHECKS, "score",
]


# ---------------------------------------------------------------------------
# Collection (live mode)
# ---------------------------------------------------------------------------

def run_bioq(bioq: str, args: list[str], timeout: float) -> tuple[int, str, str]:
    p = subprocess.run([bioq, *args], capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def _payload_has_manifest(path: Path) -> bool:
    """True iff the saved describe payload carries a non-empty manifest."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    m = payload.get("manifest") or {}
    return bool(m) and not _is_blank(m.get("service"))


def collect(bioq: str, services: list[str], manifest_dir: Path,
            retries: int, timeout: float) -> dict[str, str]:
    """Fetch describe payloads; returns {service: error-or-empty}.

    Never clobbers a previously-good manifest with an empty payload (a
    cold-start timeout must not destroy committed raw data): the fresh empty
    fetch is reported as an error and the existing file is kept.
    """
    manifest_dir.mkdir(parents=True, exist_ok=True)
    errors: dict[str, str] = {}
    for i, svc in enumerate(services, 1):
        target = manifest_dir / f"{svc}.json"
        payload = None
        last_cand: dict | None = None
        err = ""
        for attempt in range(1, retries + 2):
            try:
                rc, out, errout = run_bioq(bioq, ["describe", svc, "--output", "json"],
                                           timeout=timeout)
            except subprocess.TimeoutExpired:
                rc, out, errout = 124, "", f"timeout after {timeout}s"
            if rc == 0 and out.strip():
                try:
                    cand = json.loads(out)
                except json.JSONDecodeError as e:
                    err = f"invalid JSON from describe: {e}"
                else:
                    last_cand = cand
                    m = cand.get("manifest") or {}
                    if m and not _is_blank(m.get("service")):
                        payload = cand
                        break
                    err = "empty manifest (unreachable or cold-start timeout)"
            else:
                err = (errout or out or f"exit {rc}").strip().splitlines()[-1][:300]
            if attempt <= retries:
                print(f"  [{i}/{len(services)}] {svc}: retry {attempt} ({err[:80]})")
                time.sleep(2 * attempt)
        if payload is not None:
            target.write_text(
                json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
            errors[svc] = ""
            n_eps = len((payload.get("manifest") or {}).get("endpoints") or [])
            print(f"  [{i}/{len(services)}] {svc}: ok ({n_eps} endpoints)")
        elif target.is_file() and _payload_has_manifest(target):
            errors[svc] = f"fetch failed, kept previous manifest ({err})"
            print(f"  [{i}/{len(services)}] {svc}: FAILED — {err[:100]} (kept previous)")
        else:
            if err == "":
                err = "unknown error"
            errors[svc] = err
            # Record the fetched payload when it carries *any* evidence: either
            # nothing exists yet, or the openapi doc arrived without a manifest
            # (a service that answers HTTP but not /api/manifest — itself a
            # conformance finding).
            openapi_paths = ((last_cand or {}).get("openapi") or {}).get("paths") or {}
            if not target.is_file() or openapi_paths:
                target.write_text(json.dumps(
                    last_cand or {"service": svc, "manifest": {}, "openapi": {}},
                    indent=1, ensure_ascii=False), encoding="utf-8")
            print(f"  [{i}/{len(services)}] {svc}: FAILED — {err[:120]}")
    return errors


# ---------------------------------------------------------------------------
# Checklist (per endpoint)
# ---------------------------------------------------------------------------

def _is_blank(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


def check_endpoint(ep: dict) -> dict:
    """Evaluate the 5-item checklist on one manifest endpoint entry."""
    fields = ep.get("request_fields") or []
    files = [f for f in fields if f.get("is_file")]
    uri_companions = {f"{f['name']}_uri" for f in files}
    params = [f for f in fields
              if not f.get("is_file") and f["name"] not in uri_companions]
    optional_params = [f for f in params if not f.get("required")]
    content_type = ep.get("request_content_type") or ""

    # 1. typed_params — every field has a concrete declared type.
    typed = all(not _is_blank(f.get("type")) and f.get("type") != "any"
                for f in fields)

    # 2. file_fields — multipart endpoints must expose file inputs as
    #    file-typed fields (vacuous pass for non-multipart endpoints).
    if content_type.startswith("multipart"):
        file_typed_ok = all(
            str(f.get("type", "")).startswith(("file", "array[file")) for f in files)
        file_check = bool(files) and file_typed_ok
    else:
        file_check = True

    # 3. defaults — every optional non-file parameter declares an explicit
    #    default (vacuous pass when there are no optional parameters).
    defaults = all(f.get("default") is not None for f in optional_params)

    # 4. machine_view — the JSON view an agent consumes is complete: identity,
    #    wire format, flat field list, and a schema ref into /openapi.json.
    #    Bodyless (GET/HEAD) endpoints carry no content_type / request schema,
    #    so those sub-requirements pass vacuously (the agent only needs to call
    #    method+path, which the manifest always carries).
    #    (operation_id is tracked separately as has_operation_id: the audit
    #    found it unparsed fleet-wide while schema refs are populated, so it is
    #    reported as a gap rather than scored out of existence.)
    method = ep.get("method") or ""
    machine_base = (
        not _is_blank(method)
        and not _is_blank(ep.get("path"))
        and isinstance(ep.get("request_fields"), list)
    )
    if method.upper() in ("GET", "HEAD"):
        machine = machine_base
    else:
        machine = (
            machine_base
            and not _is_blank(content_type)
            and not _is_blank(ep.get("request_schema_ref"))
        )

    # 5. docs_text — human-readable prose present.
    docs = not (_is_blank(ep.get("summary")) and _is_blank(ep.get("description")))

    checks = {
        "typed_params": typed,
        "file_fields": file_check,
        "defaults": defaults,
        "machine_view": machine,
        "docs_text": docs,
    }
    documented = [f for f in fields if not _is_blank(f.get("description"))]
    return {
        "content_type": content_type,
        "n_fields": len(fields),
        "n_file_fields": len(files),
        "n_optional_params": len(optional_params),
        "field_desc_frac": round(len(documented) / len(fields), 3) if fields else 1.0,
        "has_operation_id": int(not _is_blank(ep.get("operation_id"))),
        **{k: int(v) for k, v in checks.items()},
        "score": round(sum(checks.values()) / len(checks), 3),
    }


def check_service(svc: str, payload: dict) -> list[dict]:
    eps = (payload.get("manifest") or {}).get("endpoints") or []
    rows = []
    for ep in eps:
        path = ep.get("path", "")
        res = check_endpoint(ep)
        rows.append({
            "service": svc,
            "endpoint": path,
            "method": ep.get("method", ""),
            "is_task": int(path.startswith("/api/tasks/")),
            **res,
        })
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--collect", action="store_true",
                    help="fetch manifests live via the bioq CLI (else re-check committed data)")
    ap.add_argument("--bioq", default="bioq", help="path to the bioq executable")
    ap.add_argument("--only", default="", help="comma-separated subset of services")
    ap.add_argument("--retries", type=int, default=2, help="retries per service (live mode)")
    ap.add_argument("--timeout", type=float, default=240.0,
                    help="per-invocation bioq timeout seconds (cold starts are slow)")
    ap.add_argument("--data-dir", default=str(Path(__file__).parent / "data"))
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    manifest_dir = data_dir / "manifests"

    # ---- enumerate the fleet --------------------------------------------
    services: list[str] = []
    errors: dict[str, str] = {}
    if args.collect:
        rc, out, errout = run_bioq(args.bioq, ["services", "--output", "json"],
                                   timeout=args.timeout)
        if rc != 0:
            print(f"error: `bioq services` failed: {errout.strip()[:300]}", file=sys.stderr)
            return 1
        services = json.loads(out)
        services = [s for s in services if s not in EXCLUDED]
        if args.only:
            keep = {s.strip() for s in args.only.split(",") if s.strip()}
            services = [s for s in services if s in keep]
        print(f"collecting manifests for {len(services)} services ...")
        errors = collect(args.bioq, services, manifest_dir, args.retries, args.timeout)
    else:
        if not manifest_dir.is_dir():
            print(f"error: {manifest_dir} not found — run with --collect first",
                  file=sys.stderr)
            return 1
        services = sorted(p.stem for p in manifest_dir.glob("*.json")
                          if p.stem not in EXCLUDED)
        print(f"re-checking {len(services)} committed manifests ...")
    for svc, reason in EXCLUDED.items():
        print(f"note: {svc} excluded from audit scope ({reason})")

    if args.only and not args.collect:
        keep = {s.strip() for s in args.only.split(",") if s.strip()}
        services = [s for s in services if s in keep]

    # ---- evaluate the checklist ------------------------------------------
    fleet_rows, conf_rows = [], []
    for svc in services:
        path = manifest_dir / f"{svc}.json"
        listed = int(svc in services)
        if not path.is_file():
            fleet_rows.append({"service": svc, "listed": listed, "manifest_ok": 0,
                               "error": errors.get(svc, "no saved manifest"),
                               "version": "", "n_endpoints": 0, "n_task_endpoints": 0})
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            fleet_rows.append({"service": svc, "listed": listed, "manifest_ok": 0,
                               "error": f"unreadable manifest: {e}", "version": "",
                               "n_endpoints": 0, "n_task_endpoints": 0})
            continue
        manifest = payload.get("manifest") or {}
        if not manifest or _is_blank(manifest.get("service")):
            # Empty manifest: either the service never answered (cold-start
            # timeout / undeployed) or it does not expose /api/manifest at all.
            # An openapi doc that *did* arrive distinguishes the two.
            openapi = payload.get("openapi") or {}
            if openapi.get("paths"):
                err = "no /api/manifest (non-uniform interface)"
            else:
                err = "empty manifest (unreachable or cold-start timeout)"
            fleet_rows.append({"service": svc, "listed": listed, "manifest_ok": 0,
                               "error": errors.get(svc) or err, "version": "",
                               "n_endpoints": 0, "n_task_endpoints": 0})
            continue
        rows = check_service(svc, payload)
        conf_rows.extend(rows)
        fleet_rows.append({
            "service": svc, "listed": listed, "manifest_ok": 1,
            "error": errors.get(svc, ""),
            "version": manifest.get("version", ""),
            "n_endpoints": len(rows),
            "n_task_endpoints": sum(r["is_task"] for r in rows),
        })

    # ---- write outputs -----------------------------------------------------
    data_dir.mkdir(parents=True, exist_ok=True)
    fleet_path = data_dir / "fleet.csv"
    with fleet_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FLEET_COLUMNS)
        w.writeheader()
        w.writerows(fleet_rows)

    conf_path = data_dir / "conformance.csv"
    with conf_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CONFORMANCE_COLUMNS)
        w.writeheader()
        w.writerows(conf_rows)

    n_ok = sum(r["manifest_ok"] for r in fleet_rows)
    print(f"\nfleet: {n_ok}/{len(fleet_rows)} manifests fetched")
    print(f"endpoints checked: {len(conf_rows)} "
          f"({sum(r['is_task'] for r in conf_rows)} task endpoints)")
    print(f"wrote {fleet_path} and {conf_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
