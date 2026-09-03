#!/usr/bin/env python3
"""Dependency sub-analysis — extract declared package dependencies from one opensource git repo.

Purpose: feed the dependency (pairwise compatibility) comparison (``analyze_compat.py``) with each
upstream tool's *declared* dependency set — the constraints the tool's own
manifests pin, without installing/resolving anything.

Output format — requirements-style text file (NOT pyproject.toml):
    A tool repo usually declares dependencies across 2-5 different manifests
    (``pyproject.toml``, ``setup.py``/``setup.cfg``, ``requirements*.txt``,
    conda ``*env*.yml|yaml``). There is no single "the pyproject.toml" to copy
    out, and fabricating one would both drop the non-pyproject sources and
    misrepresent the repo's build. A flat pip-requirements file is the natural
    *merged* view, is what ``analyze_compat.py`` already consumes, and carries
    the declared constraint verbatim (``numpy>=1.26,<2.0``) — exactly the
    information a compatibility comparison needs. Constraints from several
    files are AND-joined per package (``==1.22.4,==1.26.3``); a bare ``name``
    means any version and is dropped when a constrained mention exists.

    Lines are ``name<specifier>`` sorted by name, preceded by ``#`` provenance
    (repo, git ref, scanned source files, extraction time). Conda build hashes
    (``name=1.2.3=py39h..._0``) are stripped to valid PEP 440 specifiers.

Usage:
    python3 extract_repo_deps.py <name> <repo_dir> <output_file>
    python3 extract_repo_deps.py boltz opensource/boltz data/repo_dependency/boltz.txt
    python3 extract_repo_deps.py --git-ref <sha> IgGM opensource/IgGM out/iggm.txt

Stdlib only. ``<repo_dir>`` may be any git checkout or plain directory.
"""
from __future__ import annotations

import argparse
import ast
import configparser
import re
import subprocess
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

# Directory parts never worth scanning for dependency declarations.
_SKIP_DIR_PARTS = {
    ".git", "node_modules", ".venv", "venv", "build", "dist", "__pycache__",
    "docs", "tests", "test", "examples", "example", "data", "datasets",
    "weights", "inputs", "outputs", "img", "images", "figures",
}


def _canon(name: str) -> str:
    """PEP 503 canonical distribution name (Cython/cython, typing_extensions...)."""
    return re.sub(r"[-_.]+", "-", name).strip().lower()


def _parse_req_line(line: str) -> tuple[str, str] | None:
    """Parse one requirement/conda line -> (name, spec). spec '' = any version.

    Handles ``name``, ``name==1.2``, ``name>=1,<2``, ``name[extra]~=1.2``,
    ``name @ url`` / ``name@url`` (-> bare name, any version), conda
    ``name=1.2`` / ``name=1.2.*`` / ``name=1.2=py39h..._0`` /
    ``name==1.2=py39h..._0`` (build string dropped), ``name; marker``.
    Returns None for flags, VCS/URL lines and comments.
    """
    line = line.strip()
    if not line or line.startswith((
            "#", "-", "--", "git+", "hg+", "svn+", "bzr+",
            "http://", "https://", "file:", "ftp:")):
        return None
    if "::" in line:  # conda channel qualifier: 'nvidia::cudatoolkit' -> 'cudatoolkit'
        line = line.rsplit("::", 1)[1]
    if ";" in line:  # strip PEP 508 environment marker
        line = line.split(";", 1)[0]
    if " @" in line:  # name @ url -> name with no version constraint
        line = line.split(" @", 1)[0]
    m = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)(?:\[[^\]]*\])?\s*(.*)$", line)
    if not m:
        return None
    name, rest_raw = m.group(1), m.group(2)
    # A real requirement's version part starts with an operator (=, <, >, ~, !,
    # @). A bare word after the name — e.g. 'conda env create -f ...' or other
    # shell commands that end up in requirements/env files — is not a
    # requirement; skip it.
    if rest_raw.strip() and not rest_raw.lstrip().startswith(
            ("=", "<", ">", "~", "!", "@")):
        return None
    rest = re.sub(r"\s+", "", rest_raw)
    if not rest or rest.startswith("@"):
        # bare name, or 'name@url' (no space) -> any version; a URL pin carries
        # no PEP 440 range, so it cannot constrain a compatibility comparison
        return name, ""
    # Conda forms: '=1.2' -> '==1.2'; '=1.2=py39h..._0' / '==1.2=py39h..._0'
    # -> '==1.2' (drop the build string, which is not a PEP 440 version).
    if rest.startswith("="):
        body = rest.lstrip("=")
        m2 = re.match(r"([^=,<>~! ]+)", body)
        rest = "==" + (m2.group(1) if m2 else body)
    return name, rest


def _poetry_spec(v: str) -> str:
    """Poetry constraint -> PEP 440 (^x.y -> >=x.y,<next; ~x.y -> >=x.y,<x.y+1)."""
    v = v.strip()
    if not v or v == "*":
        return ""
    if v.startswith("^"):
        base = v[1:].strip()
        parts = [p for p in base.split(".") if p]
        if not parts:
            return ""
        if parts[0] == "0":
            upper = (f"{parts[0]}.{int(parts[1]) + 1}" if len(parts) > 1
                     else "1")
        else:
            try:
                upper = str(int(parts[0]) + 1)
            except ValueError:
                return f">={base}"
        return f">={base},<{upper}"
    if v.startswith("~"):
        base = v[1:].strip()
        parts = [p for p in base.split(".") if p]
        if not parts:
            return ""
        try:
            if len(parts) >= 2:
                upper = f"{parts[0]}.{int(parts[1]) + 1}"
            else:
                upper = str(int(parts[0]) + 1)
        except ValueError:
            return f">={base}"
        return f">={base},<{upper}"
    return v


def _pyproject_reqs(path: Path) -> list[tuple[str, str, str]]:
    """PEP 621 ``[project]`` + poetry ``[tool.poetry]`` dependencies."""
    reqs: list[tuple[str, str, str]] = []
    rel = str(path)
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except Exception:
        return reqs
    proj = data.get("project") or {}
    for spec in proj.get("dependencies") or []:
        r = _parse_req_line(str(spec))
        if r:
            reqs.append((r[0], r[1], rel))
    for _extra, specs in (proj.get("optional-dependencies") or {}).items():
        for spec in specs or []:
            r = _parse_req_line(str(spec))
            if r:
                reqs.append((r[0], r[1], rel))
    tool = data.get("tool") or {}
    poetry = tool.get("poetry") or {}
    poetry_groups: dict[str, dict] = {"dependencies": poetry.get("dependencies") or {}}
    for grp in (poetry.get("group") or {}).values():
        poetry_groups.setdefault("dependencies", {}).update(grp.get("dependencies") or {})
    for name, spec in poetry_groups["dependencies"].items():
        if _canon(name) == "python":
            continue  # the interpreter itself is tracked separately (requires-python)
        if isinstance(spec, str):
            raw = f"{name}{_poetry_spec(spec)}"
        elif isinstance(spec, dict):
            raw = f"{name}{_poetry_spec(str(spec.get('version', '*')))}"
        elif isinstance(spec, list):
            parts = [_poetry_spec(str(s)) for s in spec if s]
            raw = f"{name}{','.join(parts)}" if parts else name
        else:
            continue
        r = _parse_req_line(raw)
        if r:
            reqs.append((r[0], r[1], rel))
    return reqs


def _setup_py_reqs(path: Path) -> list[tuple[str, str, str]]:
    """``setup()`` keyword args via AST (never executes the file), regex fallback."""
    reqs: list[tuple[str, str, str]] = []
    rel = str(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        tree = None
    if tree is not None:
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "setup"):
                continue
            for kw in node.keywords:
                if kw.arg not in ("install_requires", "extras_require"):
                    continue
                lists = []
                if isinstance(kw.value, (ast.List, ast.Tuple)):
                    lists = [kw.value.elts]
                elif isinstance(kw.value, ast.Dict):
                    lists = [v.elts for v in kw.value.values
                             if isinstance(v, (ast.List, ast.Tuple))]
                for elts in lists:
                    for el in elts:
                        if isinstance(el, ast.Constant) and isinstance(el.value, str):
                            r = _parse_req_line(el.value)
                            if r:
                                reqs.append((r[0], r[1], rel))
    if not reqs:  # dynamic setup.py fallback
        for m in re.finditer(r"install_requires\s*=\s*\[(.*?)\]", text, re.S | re.I):
            for s in re.findall(r"['\"]([^'\"]+)['\"]", m.group(1)):
                r = _parse_req_line(s)
                if r:
                    reqs.append((r[0], r[1], rel))
    return reqs


def _setup_cfg_reqs(path: Path) -> list[tuple[str, str, str]]:
    reqs: list[tuple[str, str, str]] = []
    rel = str(path)
    try:
        cp = configparser.ConfigParser(interpolation=None)
        cp.read(path, encoding="utf-8")
        if cp.has_option("options", "install_requires"):
            for line in cp.get("options", "install_requires").splitlines():
                r = _parse_req_line(line)
                if r:
                    reqs.append((r[0], r[1], rel))
        if cp.has_section("options.extras_require"):
            for _k, v in cp.items("options.extras_require"):
                for line in v.splitlines():
                    r = _parse_req_line(line)
                    if r:
                        reqs.append((r[0], r[1], rel))
    except Exception:
        pass
    return reqs


def _requirements_reqs(path: Path, depth: int = 0) -> list[tuple[str, str, str]]:
    reqs: list[tuple[str, str, str]] = []
    rel = str(path)
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return reqs
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-r", "--requirement", "-c", "--constraint")):
            if depth < 2:
                parts = line.split()
                if len(parts) >= 2:
                    sub = (path.parent / parts[1]).resolve()
                    if sub.is_file():
                        reqs += _requirements_reqs(sub, depth + 1)
            continue
        r = _parse_req_line(line)
        if r:
            reqs.append((r[0], r[1], rel))
    return reqs


def _env_yml_reqs(path: Path) -> list[tuple[str, str, str]]:
    """Minimal conda environment.yml parser: ``dependencies:`` + nested ``pip:``."""
    reqs: list[tuple[str, str, str]] = []
    rel = str(path)
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return reqs
    in_deps, deps_indent, pip_mode = False, 0, False
    for raw in lines:
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        s = raw.strip()
        if s == "dependencies:":
            in_deps, deps_indent, pip_mode = True, indent, False
            continue
        if not in_deps:
            continue
        if not s.startswith("-") and indent <= deps_indent:
            in_deps = False
            continue
        if not s.startswith("-"):
            continue
        item = s[1:].strip()
        if item == "pip:":
            pip_mode = True
            continue
        if not item:
            continue
        r = _parse_req_line(item)
        if r:
            tag = "pip" if pip_mode else "conda"
            reqs.append((r[0], r[1], f"{rel}[{tag}]"))
    return reqs


def _candidate_dep_files(repo_dir: Path) -> list[Path]:
    """Dependency-declaration files in a repo, most authoritative first."""
    found: list[Path] = []
    for name in ("pyproject.toml", "setup.py", "setup.cfg"):
        p = repo_dir / name
        if p.is_file():
            found.append(p)
    for pat in ("requirements*.txt", "*env*.yml", "*env*.yaml"):
        for p in repo_dir.rglob(pat):
            if not p.is_file():
                continue
            rel = p.relative_to(repo_dir)
            if len(rel.parts) > 4:
                continue
            if any(part in _SKIP_DIR_PARTS for part in rel.parts[:-1]):
                continue
            found.append(p)
    seen: set[str] = set()
    out: list[Path] = []
    for p in found:
        key = str(p.resolve())
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def extract_repo_deps(repo_dir: Path) -> tuple[dict[str, tuple[str, str]], list[str]]:
    """Parse all dependency declarations in one repo.

    Returns (cname -> (display_name, joined_spec), [scanned source files]).
    """
    reqs: list[tuple[str, str, str]] = []
    files: list[str] = []
    for f in _candidate_dep_files(repo_dir):
        rel = str(f.relative_to(repo_dir))
        files.append(rel)
        if f.name == "pyproject.toml":
            reqs += _pyproject_reqs(f)
        elif f.name == "setup.py":
            reqs += _setup_py_reqs(f)
        elif f.name == "setup.cfg":
            reqs += _setup_cfg_reqs(f)
        elif f.name.startswith("requirements") and f.suffix == ".txt":
            reqs += _requirements_reqs(f)
        elif f.suffix in (".yml", ".yaml"):
            reqs += _env_yml_reqs(f)

    merged: dict[str, list[str]] = {}
    display: dict[str, str] = {}
    for name, spec, _src in reqs:
        cname = _canon(name)
        display.setdefault(cname, name)
        if spec:
            lst = merged.setdefault(cname, [])
            if spec not in lst:
                lst.append(spec)
        else:
            merged.setdefault(cname, [])
    return ({c: (display[c], ",".join(lst)) for c, lst in merged.items()},
            sorted(files))


def git_head(repo_dir: Path) -> str:
    """Best-effort current commit ('' if not a git checkout)."""
    try:
        r = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=30, check=False)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def write_dep_file(path: Path, name: str, merged: dict[str, tuple[str, str]],
                   source_files: list[str], ref: str,
                   requires_python: str = "") -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = [
        f"# repo: {name}",
        f"# git-ref: {ref}" if ref else "# git-ref: -",
        f"# source_files: {', '.join(source_files) if source_files else '-'}",
        f"# packages: {len(merged)}",
        f"# extracted: {ts}",
        "# source: declared dependencies from opensource git checkout",
        "#         (PEP 621/poetry pyproject.toml, setup.py/cfg, requirements*, conda env)",
        "# note: constraints AND-joined per package; alternative variant files",
        "#       (e.g. cuda121/cuda124) are not distinguished; conda build",
        "#       hashes stripped to PEP 440",
        "",
    ]
    if requires_python:
        header.insert(3, f"# requires-python: {requires_python}")
    lines = []
    for cname in sorted(merged):
        disp, spec = merged[cname]
        lines.append(f"{disp}{spec}" if spec else disp)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(header) + ("\n".join(lines) + "\n" if lines else ""),
                    encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="display name for this repo (e.g. boltz, IgGM)")
    ap.add_argument("repo_dir", help="path to the opensource git checkout")
    ap.add_argument("output_file", help="requirements-style output file to write")
    ap.add_argument("--git-ref", default="",
                    help="commit/ref to record in the header (default: git HEAD)")
    ap.add_argument("--quiet", action="store_true", help="suppress the summary line")
    args = ap.parse_args()

    repo_dir = Path(args.repo_dir).expanduser().resolve()
    if not repo_dir.is_dir():
        raise SystemExit(f"repo dir not found: {repo_dir}")

    merged, files = extract_repo_deps(repo_dir)
    ref = args.git_ref or git_head(repo_dir)

    requires_python = ""
    pp = repo_dir / "pyproject.toml"
    if pp.is_file():
        try:
            with pp.open("rb") as f:
                requires_python = (tomllib.load(f).get("project") or {}).get(
                    "requires-python", "") or ""
        except Exception:
            requires_python = ""

    out = Path(args.output_file).expanduser()
    write_dep_file(out, args.name, merged, files, ref, requires_python)

    if not args.quiet:
        print(f"[{'OK' if merged else 'EMPTY'}] {args.name}: {len(merged)} packages "
              f"from {len(files)} file(s) -> {out}"
              + (f"  (git {ref})" if ref else "")
              + (f"  [requires-python {requires_python}]" if requires_python else ""))


if __name__ == "__main__":
    main()
