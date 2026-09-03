#!/usr/bin/env python3
"""Dependency sub-analysis — extract the real, fully-resolved pip dependency set per service.

For every ``bioq-services/services/<svc>-server/`` we locate its built Docker image
and enumerate installed distributions *inside* the image (via importlib.metadata),
using the interpreter that actually runs the service. The result is one
requirements-style (``name==version``) file per service in
``data/service_dependency/<svc>.txt`` (``name==version`` lines + provenance header).

Why the image and not the Dockerfile: a service's real stack (torch, the upstream
tool, transitive deps) is installed by Dockerfile ``RUN`` lines / conda envs / git+
installs, *not* declared in ``pyproject.toml`` (which only lists the wrapper). Only
the built image knows the resolved versions — including transitive deps, which are
where most incompatibilities hide. See ../README.md.

Interpreter selection (per image), in order:
  1. The python named in the image's ENTRYPOINT/CMD (authoritative — that's what
     runs the service), resolved against WorkingDir. From ``docker inspect``.
  2. Fallback: scan common roots inside the container for python interpreters and
     pick the one with the most installed packages (the heavy app env, not a
     minimal base). Handles odd layouts and conda envs generically.

Run this on a host that has all the images (e.g. ECS):

    python3 extract_deps.py                      # bare local tags (<svc>:<VERSION>/latest)
    python3 extract_deps.py --registry harbor.ruosheng.bio/aliyun_fc
    python3 extract_deps.py --list-only          # dry-run: show resolved image per svc
    python3 extract_deps.py --services boltz-server,dockq-server

Outputs:
  data/service_dependency/<svc>.txt   — pip freeze + provenance header, per service
  data/extraction_manifest.csv        — service, image, status, interpreter, n_pkgs, error

Stdlib only; shells out to ``docker``. No cloud/network access needed beyond having
the images present (pull them first if using --registry).
"""
from __future__ import annotations

import argparse
import csv
import json
import posixpath
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent  # .../dependency_incompatibility


def _find_services_root(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if not p.exists():
            raise SystemExit(f"--services-root not found: {p}")
        return p
    # Walk upward looking for bioq-services/services.
    for base in [HERE, *HERE.parents]:
        cand = base / "bioq-services" / "services"
        if cand.is_dir():
            return cand
    raise SystemExit(
        "could not locate bioq-services/services; pass --services-root explicitly"
    )


# In-container interpreter discovery + dependency listing. POSIX sh. $PYHINT =
# preferred interpreter path (may be empty). Prints two provenance comment lines
# then ``name==version`` lines. Redirection (not a pipe) keeps loop vars in the
# current shell.
#
# We enumerate installed distributions via ``importlib.metadata`` rather than
# ``pip freeze``: the services' app environments are uv-created venvs that ship
# WITHOUT pip, so ``python -m pip`` fails there and the scan would wrongly fall
# back to a minimal base interpreter. importlib.metadata is in every Python 3.8+
# and yields the same pip-installable ``name==version`` form.
CONTAINER_SNIPPET = r"""
set -u
cat > /tmp/lister.py <<'PYEOF'
import importlib.metadata as md
seen = {}
for d in md.distributions():
    try:
        name = d.metadata["Name"]
    except Exception:
        name = None
    if not name:
        continue
    seen[name] = d.version
for n in sorted(seen, key=str.lower):
    print(f"{n}=={seen[n]}")
PYEOF

cand=/tmp/.pycands
: > "$cand"
[ -n "${PYHINT:-}" ] && printf '%s\n' "$PYHINT" >> "$cand"
command -v python3 2>/dev/null >> "$cand" || true
command -v python  2>/dev/null >> "$cand" || true
find /opt /usr/local /usr/bin /app /workspace /root /home /.venv /venv \
    -maxdepth 6 -type f \( -name python -o -name python3 \) 2>/dev/null >> "$cand" || true

bestpy=""; bestc=-1; bestout=""
while IFS= read -r py; do
    [ -n "$py" ] || continue
    [ -x "$py" ] || continue
    out=$("$py" /tmp/lister.py 2>/dev/null) || continue
    c=$(printf '%s\n' "$out" | grep -c '==' 2>/dev/null || printf 0)
    if [ "$c" -gt "$bestc" ]; then bestc=$c; bestpy=$py; bestout=$out; fi
done < "$cand"

printf '# interpreter=%s\n' "$bestpy"
printf '# packages=%s\n' "$bestc"
[ -n "$bestout" ] && printf '%s\n' "$bestout"
"""


def _run(cmd: list[str], timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, check=False
    )


def _image_exists(ref: str) -> dict | None:
    """Return the image's Config dict if present locally, else None."""
    r = _run(["docker", "image", "inspect", ref], timeout=60)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)[0].get("Config", {}) or {}
    except (json.JSONDecodeError, IndexError, KeyError):
        return {}


def _candidate_refs(svc: str, version: str | None, registry: str | None,
                    tag: str | None) -> list[str]:
    reg = registry.rstrip("/") + "/" if registry else ""
    tags: list[str] = []
    if tag:
        tags = [tag]
    else:
        if version:
            tags.append(version)
        tags.append("latest")
    refs: list[str] = []
    # Prefer registry-qualified (matches a pulled fleet), then bare local tags.
    for t in tags:
        if reg:
            refs.append(f"{reg}{svc}:{t}")
    for t in tags:
        refs.append(f"{svc}:{t}")
    if not tag:
        refs.append(svc)  # bare, no tag (docker defaults to :latest)
    # de-dupe preserving order
    seen: set[str] = set()
    return [r for r in refs if not (r in seen or seen.add(r))]


def _resolve_image(svc: str, version: str | None, registry: str | None,
                   tag: str | None) -> tuple[str | None, dict]:
    for ref in _candidate_refs(svc, version, registry, tag):
        cfg = _image_exists(ref)
        if cfg is not None:
            return ref, cfg
    return None, {}


def _hint_python(cfg: dict) -> str:
    """Extract the service interpreter path from ENTRYPOINT/CMD, resolved against
    WorkingDir. Returns '' if none obvious (the container scan then takes over)."""
    tokens = (cfg.get("Entrypoint") or []) + (cfg.get("Cmd") or [])
    workdir = cfg.get("WorkingDir") or "/"
    py = ""
    for t in tokens:
        if re.search(r"(^|/)python[0-9.]*$", t):
            py = t
            break
    if py and not py.startswith("/"):
        py = posixpath.normpath(posixpath.join(workdir, py))
    return py


def _extract(ref: str, hint: str, timeout: int) -> tuple[str, str, int]:
    """Run the container snippet. Returns (freeze_body, interpreter, n_pkgs)."""
    r = _run(
        ["docker", "run", "--rm", "-e", f"PYHINT={hint}",
         "--entrypoint", "/bin/sh", ref, "-c", CONTAINER_SNIPPET],
        timeout=timeout,
    )
    if r.returncode != 0 and not r.stdout.strip():
        raise RuntimeError((r.stderr or "docker run failed").strip()[:500])
    interp, n_pkgs, body = "", -1, []
    for line in r.stdout.splitlines():
        if line.startswith("# interpreter="):
            interp = line.split("=", 1)[1].strip()
        elif line.startswith("# packages="):
            try:
                n_pkgs = int(line.split("=", 1)[1].strip())
            except ValueError:
                n_pkgs = -1
        elif line.strip():
            body.append(line.rstrip())
    return "\n".join(body), interp, n_pkgs


def _write_service_file(out_dir: Path, svc: str, ref: str, interp: str,
                        n_pkgs: int, body: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = [
        f"# service: {svc}",
        f"# image: {ref}",
        f"# interpreter: {interp}",
        f"# packages: {n_pkgs}",
        f"# extracted: {ts}",
        "# source: importlib.metadata inside image (pip-style name==version)",
        "",
    ]
    (out_dir / f"{svc}.txt").write_text(
        "\n".join(header) + (body + "\n" if body else ""), encoding="utf-8"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--registry", default="",
                    help="registry prefix, e.g. harbor.ruosheng.bio/aliyun_fc")
    ap.add_argument("--tag", default="",
                    help="force a single image tag (overrides VERSION/latest)")
    ap.add_argument("--services", default="",
                    help="comma-separated subset of service dir names")
    ap.add_argument("--services-root", default="",
                    help="path to bioq-services/services (auto-detected otherwise)")
    ap.add_argument("--output-dir", default=str(HERE / "data" / "service_dependency"))
    ap.add_argument("--timeout", type=int, default=600,
                    help="per-image docker-run timeout in seconds")
    ap.add_argument("--list-only", action="store_true",
                    help="dry-run: resolve and print image per service, no extraction")
    args = ap.parse_args()

    root = _find_services_root(args.services_root or None)
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    wanted = {s.strip() for s in args.services.split(",") if s.strip()}
    svc_dirs = sorted(
        p for p in root.iterdir()
        if p.is_dir() and (p / "Dockerfile").exists()
        and (not wanted or p.name in wanted)
    )
    if not svc_dirs:
        raise SystemExit(f"no services with a Dockerfile under {root}")

    registry = args.registry or None
    tag = args.tag or None
    manifest: list[dict] = []

    for d in svc_dirs:
        svc = d.name
        version = None
        vf = d / "VERSION"
        if vf.exists():
            version = vf.read_text(encoding="utf-8").strip() or None

        ref, cfg = _resolve_image(svc, version, registry, tag)
        if ref is None:
            tried = ", ".join(_candidate_refs(svc, version, registry, tag))
            print(f"[MISSING] {svc}: no image found (tried: {tried})", file=sys.stderr)
            manifest.append({"service": svc, "image": "", "status": "missing",
                             "interpreter": "", "n_packages": "", "error": "no image"})
            continue

        hint = _hint_python(cfg)
        if args.list_only:
            print(f"{svc:<26} -> {ref}   (hint python: {hint or '-'})")
            manifest.append({"service": svc, "image": ref, "status": "resolved",
                             "interpreter": hint, "n_packages": "", "error": ""})
            continue

        try:
            body, interp, n_pkgs = _extract(ref, hint, args.timeout)
        except (subprocess.TimeoutExpired, RuntimeError) as e:
            print(f"[ERROR]   {svc} ({ref}): {e}", file=sys.stderr)
            manifest.append({"service": svc, "image": ref, "status": "error",
                             "interpreter": "", "n_packages": "", "error": str(e)[:200]})
            continue

        status = "ok" if n_pkgs > 0 else "empty"
        _write_service_file(out_dir, svc, ref, interp, n_pkgs, body)
        print(f"[{status.upper():<5}] {svc:<26} {ref}  py={interp or '-'}  n={n_pkgs}")
        manifest.append({"service": svc, "image": ref, "status": status,
                         "interpreter": interp, "n_packages": n_pkgs, "error": ""})

    man_path = out_dir.parent / "extraction_manifest.csv"
    with man_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["service", "image", "status",
                                          "interpreter", "n_packages", "error"])
        w.writeheader()
        w.writerows(manifest)

    ok = sum(1 for m in manifest if m["status"] == "ok")
    print(f"\n{ok}/{len(manifest)} services extracted -> "
          f"{out_dir}  (manifest: {man_path.name})")


if __name__ == "__main__":
    main()
