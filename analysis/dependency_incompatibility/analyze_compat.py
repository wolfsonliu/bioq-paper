#!/usr/bin/env python3
"""Dependency sub-analysis — pairwise co-installability analysis across service envs.

Question: can two services' Python environments be merged into ONE environment
(shared interpreter + site-packages) without a version conflict? This is the crux
of the "dependency incompatibility" claim — each service ships its own container
precisely because their stacks cannot co-exist.

Inputs (--dep-dir) can be either of the two extractions from this directory:

* ``data/service_dependency/`` (image mode) — fully-resolved, fully-pinned envs:
  every installed distribution as ``name==version``. Comparing these answers
  "can the two frozen envs share one venv exactly as-is?".
* ``data/repo_dependency/`` (repo mode) — the tools' *declared* constraints
  (``name>=1.26,<2.0``, ``name==2.3.*``, bare ``name`` = any). Comparing these
  answers the resolver question: "does a single version exist that satisfies both
  tools' declared requirements?" (SpecifierSet intersection, exact for the
  intervals real pins form).

Two notions of "compatible" (we report both — a pinned diff is not always a real
incompatibility):
  * co-installable (strict): can the two envs share ONE venv exactly as-is? Only
    one version of a package can be installed, so ANY shared-package spec
    difference blocks this. The correct test for literally merging services.
  * reconcilable (graded): could a *single* version satisfy both if we were free
    to bump pins? For exact pins we grade the version difference by semantic
    distance (see ``_severity``): major / CUDA-build diffs = HARD
    (irreconcilable); minor / patch diffs = SOFT (a coordinated bump likely
    fixes). For declared constraints we test SpecifierSet intersection: disjoint
    ranges = HARD (no version can satisfy both); overlapping-but-different = SOFT.

Method — direct spec comparison (exact for our inputs):
    Image mode: every transitive constraint that would conflict is already
    materialised as a concrete pin in both sets. What the exact pins CANNOT tell
    us is the true allowable *range* of each service (only its one frozen point),
    so the SOFT class is a "likely reconcilable" estimate, not a proof; the HARD
    class is a firm lower bound on genuine incompatibility.
    Repo mode: constraints are compared with ``packaging.specifiers.SpecifierSet``
    (``&`` intersection, emptiness probed at boundary-anchored candidate
    versions). A shared package is a HARD conflict iff no version satisfies both
    declared constraints.

Why not (only) a resolver like uv:
    ``uv pip compile <reqA> <reqB>`` also detects genuine clashes, but it is the
    wrong primary tool here. Two exact ``==`` pins at different versions can only be
    confirmed, not negotiated, so on frozen inputs uv's best case merely reproduces
    the set verdict — slower and needing network. Worse, these environments contain
    packages that are NOT on the public index: the private ``bioagent-service-
    framework`` (shared by every service), CUDA-local ``torch==...+cuXXX`` builds,
    and conda-only scientific packages. uv reports those as "not found in the
    package registry" and fails the whole resolution, conflating *unavailability*
    with *incompatibility* (false conflicts on genuinely mergeable pairs). The set
    method has neither problem. ``--uv-verify`` runs uv on a sample purely to
    demonstrate this: it classifies uv outcomes as compatible / conflict /
    inconclusive (non-PyPI pin) and shows uv agrees with the set method on every
    pair it can actually judge. (A resolver *would* add value if we fed original
    version *ranges*, but those live only in each tool's upstream install, not in a
    single declarable file — hence we compare resolved envs.)

Outputs (under --out-dir; the two views are kept in separate dirs):
  frozen   view -> data/frozen/    (analysis of data/service_dependency/, i.e. image envs)
  declared view -> data/declared/  (analysis of data/repo_dependency/, i.e. repo constraints)
  Each dir receives:
    pairwise_compat.csv        service_a, service_b, n_shared, n_conflict, n_hard, n_soft,
                               coinstallable, reconcilable, hard_conflict_packages
    conflict_matrix.csv        NxN matrix of n_hard conflict counts (0 = mergeable)
    package_fragmentation.csv  package, n_services, n_versions, conflicting_pairs,
                               versions   (root-cause: which packages drive conflicts)

Usage:
    python3 analyze_compat.py                                  # frozen -> data/frozen/
    python3 analyze_compat.py --dep-dir data/repo_dependency \
        --out-dir data/declared                                # declared -> data/declared/
    python3 analyze_compat.py --uv-verify                      # sample cross-check (needs net)
    python3 analyze_compat.py --uv-verify --uv-pairs boltz-server:dockq-server

Core analysis is stdlib-only; constraint comparison additionally needs ``packaging``
(``uv run --with packaging python analyze_compat.py``).
"""
from __future__ import annotations

import argparse
import csv
import itertools
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _canon(name: str) -> str:
    """PEP 503 canonical distribution name (Cython/cython, typing_extensions -> ...)."""
    return re.sub(r"[-_.]+", "-", name).strip().lower()


def _parse_ver(v: str) -> tuple[tuple[int, ...], str]:
    """Return (release_tuple, local/build). '2.3.1+cu121' -> ((2,3,1), 'cu121')."""
    local = ""
    if "+" in v:
        v, local = v.split("+", 1)
    m = re.match(r"(\d+(?:\.\d+)*)", v)
    rel = tuple(int(x) for x in m.group(1).split(".")) if m else ()
    return rel, local


def _severity(va: str, vb: str) -> str | None:
    """Grade a version difference. None if identical.

    build  differing local/CUDA build tag (+cuXXX) — ABI-specific, irreconcilable
    major  differing major (or, for 0.x, differing minor — 0.x minors are breaking)
    minor  same major, differing minor    — usually reconcilable by a bump
    patch  same major.minor, differing rest (patch/post/pre) — trivially reconcilable

    'build' and 'major' are treated as HARD (no single version satisfies both);
    'minor' and 'patch' are SOFT (a coordinated version bump likely reconciles them).
    """
    if va == vb:
        return None
    (ra, la), (rb, lb) = _parse_ver(va), _parse_ver(vb)
    if la != lb and (la or lb):
        return "build"
    ra = ra + (0,) * (3 - len(ra)) if len(ra) < 3 else ra
    rb = rb + (0,) * (3 - len(rb)) if len(rb) < 3 else rb
    if ra[0] != rb[0]:
        return "major"
    if ra[0] == 0 and ra[1] != rb[1]:
        return "major"
    if ra[1] != rb[1]:
        return "minor"
    return "patch"


_HARD = {"build", "major", "range"}


def _parse_spec(line: str) -> tuple[str, str] | None:
    """Parse a dep-file line -> (canonical_name, spec). spec '' = any version.

    Accepts both frozen (``name==1.26.3``) and declared (``name>=1.26,<2.0``,
    ``name~=1.2``, bare ``name``) lines. Canonicalises the name.
    """
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    m = re.match(
        r"^([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?"
        r"(?:\s*(==|!=|<=|>=|<|>|~=|===|=)\s*(.*))?$",
        line,
    )
    if not m:
        return None
    name, op, rest = m.group(1), m.group(2) or "", (m.group(3) or "").strip()
    if not op:
        return _canon(name), ""
    rest = re.sub(r"\s+", "", rest)
    if op == "=":  # conda-style single '='
        op = "=="
    return _canon(name), op + rest


def _is_pin(spec: str) -> bool:
    """True if spec is an exact pinned version (``==1.2.3`` / ``==1.2.3+cu121``)."""
    return spec.startswith("==") and "," not in spec and "*" not in spec


def _fmt(spec: str) -> str:
    """Display form: bare version for pins, the constraint otherwise ('*' = any)."""
    return spec[2:] if _is_pin(spec) else (spec or "*")


def _specs_intersect(sa: str, sb: str) -> bool:
    """Do two declared specifier sets admit a common version? (packaging)

    Exact for the intervals real pins form; emptiness is probed at
    boundary-anchored candidate versions (each boundary, one micro-step above it,
    +/-1 bumps on every segment, plus a fixed spread). Without ``packaging`` we
    assume compatible (conservative — never invents a conflict).
    """
    try:
        from packaging.specifiers import InvalidSpecifier, SpecifierSet
        from packaging.version import InvalidVersion
    except ImportError:
        return True

    def _ss(s: str) -> SpecifierSet | None:
        s = s.strip()
        if not s or s == "*":
            return SpecifierSet("")
        try:
            return SpecifierSet(s)
        except InvalidSpecifier:
            return None

    a, b = _ss(sa), _ss(sb)
    if a is None or b is None:
        return True
    if not str(a) or not str(b):
        return True  # 'any' on either side intersects everything
    inter = a & b
    cands: set[str] = set()
    for s in inter:
        v = s.version
        cands.add(v)
        cands.add(v + ".1")  # just above the boundary
        parts = v.split(".")
        for i in range(len(parts)):
            try:
                n = int(parts[i])
            except ValueError:
                continue
            for delta in (1, -1):
                q = list(parts)
                q[i] = str(n + delta)
                cands.add(".".join(q))
    cands |= {"0.0.1", "0.1", "1.0", "1.0.0", "1.5", "2.0", "2.0.0",
              "3.0", "10.0", "99.0", "99.0.0"}
    for c in cands:
        try:
            if inter.contains(c):
                return True
        except InvalidVersion:
            continue
    return False


def _grade(va: str, vb: str) -> str | None:
    """Severity of a spec difference. None if the two specs are identical.

    exact-vs-exact -> semantic-distance grading (build/major/minor/patch)
    otherwise      -> SpecifierSet intersection: 'range' (HARD, disjoint) or
                      'overlap' (SOFT, a common version exists but specs differ)
    """
    if va == vb:
        return None
    if _is_pin(va) and _is_pin(vb):
        return _severity(va[2:], vb[2:])
    return "range" if not _specs_intersect(va, vb) else "overlap"


def load_service_deps(dep_dir: Path) -> dict[str, dict[str, str]]:
    """service -> {canonical_name: spec}. spec '' = any version."""
    out: dict[str, dict[str, str]] = {}
    for f in sorted(dep_dir.glob("*.txt")):
        svc = f.name[:-4]
        pkgs: dict[str, str] = {}
        for line in f.read_text(encoding="utf-8").splitlines():
            r = _parse_spec(line)
            if r is None:
                continue
            cname, spec = r
            pkgs[cname] = spec
            _DISPLAY.setdefault(cname, _display_name(line, cname))
        if pkgs:
            out[svc] = pkgs
    return out


def _display_name(line: str, cname: str) -> str:
    """Human-readable name for a parsed line (best-effort)."""
    m = re.match(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)", line)
    return m.group(1) if m else cname


_DISPLAY: dict[str, str] = {}


def pairwise(deps: dict[str, dict[str, str]]) -> list[dict]:
    rows: list[dict] = []
    for a, b in itertools.combinations(sorted(deps), 2):
        pa, pb = deps[a], deps[b]
        shared = pa.keys() & pb.keys()
        graded = [(n, _grade(pa[n], pb[n])) for n in sorted(shared)]
        graded = [(n, s) for n, s in graded if s is not None]
        hard = [n for n, s in graded if s in _HARD]
        soft = [n for n, s in graded if s not in _HARD]
        hard_detail = "; ".join(
            f"{_DISPLAY.get(n, n)}({_fmt(pa[n])}|{_fmt(pb[n])}:{s})"
            for n, s in graded if s in _HARD
        )
        rows.append({
            "service_a": a,
            "service_b": b,
            "n_shared": len(shared),
            "n_conflict": len(graded),   # any spec difference (strict merge)
            "n_hard": len(hard),         # irreconcilable (major/build/disjoint)
            "n_soft": len(soft),         # reconcilable by a bump / overlapping range
            "coinstallable": len(graded) == 0,   # can literally share one venv as-is
            "reconcilable": len(hard) == 0,       # no hard conflict -> a common set may exist
            "hard_conflict_packages": hard_detail,
        })
    return rows


def package_fragmentation(deps: dict[str, dict[str, str]]) -> list[dict]:
    """Per package: spec spread + how many service pairs it puts in conflict."""
    by_pkg: dict[str, dict[str, int]] = {}  # cname -> {spec: n_services}
    for pkgs in deps.values():
        for cname, spec in pkgs.items():
            by_pkg.setdefault(cname, {})
            by_pkg[cname][spec] = by_pkg[cname].get(spec, 0) + 1

    rows: list[dict] = []
    for cname, specs in by_pkg.items():
        n_services = sum(specs.values())
        total_pairs = n_services * (n_services - 1) // 2
        same_ver_pairs = sum(c * (c - 1) // 2 for c in specs.values())
        conflicting_pairs = total_pairs - same_ver_pairs
        ver_str = "|".join(
            f"{_fmt(s)}:{c}" for s, c in sorted(specs.items(), key=lambda kv: -kv[1])
        )
        rows.append({
            "package": _DISPLAY.get(cname, cname),
            "n_services": n_services,
            "n_versions": len(specs),
            "conflicting_pairs": conflicting_pairs,
            "versions": ver_str,
        })
    rows.sort(key=lambda r: (-r["conflicting_pairs"], -r["n_versions"], r["package"]))
    return rows


def write_matrix(deps: dict[str, dict[str, str]], pair_rows: list[dict],
                 path: Path, key: str = "n_hard") -> None:
    svcs = sorted(deps)
    conflict = {(r["service_a"], r["service_b"]): r[key] for r in pair_rows}
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["service", *svcs])
        for a in svcs:
            row = [a]
            for b in svcs:
                if a == b:
                    row.append(0)
                else:
                    key = (a, b) if (a, b) in conflict else (b, a)
                    row.append(conflict.get(key, 0))
            w.writerow(row)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


# --- optional uv cross-check ---------------------------------------------------

_UV_NOT_ON_INDEX = re.compile(
    r"not found in the package registry|was not found|no versions? .* found",
    re.IGNORECASE,
)


def _uv_verdict(returncode: int, stderr: str) -> str:
    """Classify a uv resolution outcome: compatible | conflict | inconclusive.

    'inconclusive' = uv could not judge because a pinned package is not on the
    configured index (private framework, CUDA-local ``+cuXXX`` torch, conda-only
    scientific packages). That is an *availability* failure, not a version clash,
    so it must not be counted as a conflict.
    """
    if returncode == 0:
        return "compatible"
    if _UV_NOT_ON_INDEX.search(stderr or ""):
        return "inconclusive"
    return "conflict"


def uv_verify(deps: dict[str, dict[str, str]], pairs: list[tuple[str, str]]) -> None:
    if not pairs:
        return
    print("\n=== uv cross-check (independent resolver verdict) ===")
    print("note: uv can only judge pairs whose pins are all on the index; pairs with\n"
          "      private/CUDA-local/conda-only pins come back 'inconclusive'.")
    agree = disagree = 0
    for a, b in pairs:
        if a not in deps or b not in deps:
            print(f"  {a} x {b}: skip (unknown service)")
            continue
        with tempfile.TemporaryDirectory() as td:
            ra = Path(td) / "a.txt"
            rb = Path(td) / "b.txt"
            ra.write_text("\n".join(f"{_DISPLAY.get(n, n)}{spec}"
                                    for n, spec in deps[a].items()), encoding="utf-8")
            rb.write_text("\n".join(f"{_DISPLAY.get(n, n)}{spec}"
                                    for n, spec in deps[b].items()), encoding="utf-8")
            try:
                r = subprocess.run(
                    ["uv", "pip", "compile", "--no-deps", "--quiet",
                     "-o", str(Path(td) / "out.txt"), str(ra), str(rb)],
                    capture_output=True, text=True, timeout=300, check=False,
                )
            except FileNotFoundError:
                print("  uv not found on PATH — install uv to use --uv-verify")
                return
            except subprocess.TimeoutExpired:
                print(f"  {a} x {b}: uv timed out")
                continue
        uv_v = _uv_verdict(r.returncode, r.stderr)
        shared = deps[a].keys() & deps[b].keys()
        set_v = ("compatible" if not any(_grade(deps[a][n], deps[b][n]) in _HARD
                                        for n in shared) else "conflict")
        if uv_v == "inconclusive":
            tag = "n/a"
        elif uv_v == set_v:
            tag = "MATCH"
            agree += 1
        else:
            tag = "MISMATCH"
            disagree += 1
        print(f"  {a} x {b}: uv={uv_v:<12} set={set_v:<10} [{tag}]")
    total = agree + disagree
    if total:
        print(f"\nuv agreed with set method on {agree}/{total} judgeable pairs "
              f"(others inconclusive: non-PyPI pins).")


def _sample_pairs(pair_rows: list[dict], n_each: int) -> list[tuple[str, str]]:
    conf = [(r["service_a"], r["service_b"]) for r in pair_rows if not r["coinstallable"]]
    comp = [(r["service_a"], r["service_b"]) for r in pair_rows if r["coinstallable"]]
    return conf[:n_each] + comp[:n_each]


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dep-dir", default=str(HERE / "data" / "service_dependency"),
                    help="dir of per-service dep files "
                         "(frozen: data/service_dependency; declared: data/repo_dependency)")
    ap.add_argument("--out-dir", default=str(HERE / "data" / "frozen"),
                    help="dir for the 3 output CSVs "
                         "(frozen: data/frozen; declared: data/declared)")
    ap.add_argument("--uv-verify", action="store_true",
                    help="cross-check a sample of pairs with the uv resolver (needs net)")
    ap.add_argument("--uv-pairs", default="",
                    help="explicit pairs 'a:b,c:d' for --uv-verify (else auto-sample)")
    ap.add_argument("--uv-sample", type=int, default=3,
                    help="pairs per class (conflict/compatible) to auto-sample")
    ap.add_argument("--ignore", default="",
                    help="comma-separated packages to drop before analysis, e.g. "
                         "'pip,setuptools,wheel' (build tools, not runtime deps)")
    args = ap.parse_args()

    dep_dir = Path(args.dep_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    deps = load_service_deps(dep_dir)
    ignore = {_canon(x) for x in args.ignore.split(",") if x.strip()}
    if ignore:
        deps = {s: {n: v for n, v in p.items() if n not in ignore}
                for s, p in deps.items()}
        print(f"ignoring {len(ignore)} package(s): {', '.join(sorted(ignore))}")
    if len(deps) < 2:
        raise SystemExit(f"need >=2 service dep files in {dep_dir} (found {len(deps)})")

    pair_rows = pairwise(deps)
    frag_rows = package_fragmentation(deps)

    _write_csv(out_dir / "pairwise_compat.csv",
               ["service_a", "service_b", "n_shared", "n_conflict", "n_hard",
                "n_soft", "coinstallable", "reconcilable",
                "hard_conflict_packages"], pair_rows)
    write_matrix(deps, pair_rows, out_dir / "conflict_matrix.csv", key="n_hard")
    _write_csv(out_dir / "package_fragmentation.csv",
               ["package", "n_services", "n_versions", "conflicting_pairs",
                "versions"], frag_rows)

    # console summary
    n_svc = len(deps)
    total = len(pair_rows)
    not_coinstall = sum(1 for r in pair_rows if not r["coinstallable"])
    hard = sum(1 for r in pair_rows if not r["reconcilable"])
    soft_only = not_coinstall - hard
    print(f"services analysed: {n_svc}   pairs: {total}")
    print(f"  not co-installable as-is (any version diff):   "
          f"{not_coinstall}/{total} ({100 * not_coinstall / total:.1f}%)")
    print(f"  HARD-incompatible (major/CUDA-build diff):     "
          f"{hard}/{total} ({100 * hard / total:.1f}%)")
    print(f"  soft-only (minor/patch — reconcilable by bump): "
          f"{soft_only}/{total} ({100 * soft_only / total:.1f}%)")
    print(f"  fully compatible (identical shared pins):       "
          f"{total - not_coinstall}/{total}")
    print("\ntop conflict-driving packages (package  versions  conflicting_pairs):")
    for r in [r for r in frag_rows if r["conflicting_pairs"] > 0][:15]:
        print(f"  {r['package']:<22} {r['n_versions']:>2} vers  "
              f"{r['conflicting_pairs']:>4} pairs   {r['versions']}")
    print(f"\nwrote pairwise_compat.csv, conflict_matrix.csv, "
          f"package_fragmentation.csv -> {out_dir}")

    if args.uv_verify:
        if args.uv_pairs:
            pairs = [tuple(p.split(":", 1)) for p in args.uv_pairs.split(",") if ":" in p]
        else:
            pairs = _sample_pairs(pair_rows, args.uv_sample)
        uv_verify(deps, pairs)


if __name__ == "__main__":
    main()
