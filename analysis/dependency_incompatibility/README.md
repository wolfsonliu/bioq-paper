# Dependency-incompatibility audit

**Role:** headline experiment. **Feasibility:** computable now (static analysis +
image inspection + a few timed builds). No cloud required.

Proves that the **38-service bioq-services fleet cannot be collapsed into one
environment**: its individual Python environments are mutually incompatible at the
package-pin level, whereas the bioq client is a dependency-light install (`httpx`
as its only direct runtime dependency, no GPU).

## Claim

Native access to the fleet means operating **many mutually incompatible Python /
GPU software stacks**; bioq collapses this to a single dependency-light client
(`httpx` only, no GPU). Therefore the fleet-of-containers + gateway design is not
a convenience — it is *necessary*, and bioq is what makes the necessity invisible
to the user.

## Rationale

A resource paper's central risk is the reviewer asking "why not just pip-install
these tools?" This experiment answers empirically: you cannot. The pins are ABI-
and major-incompatible (torch spans **1.12 → 2.12** across CUDA 11 and 12; core
libraries such as numpy / scipy / pandas are pinned at many mutually-irreconcilable
versions), so no single environment can host more than a small subset of the fleet.

The experiment reports the incompatibility at two complementary levels, from
coarse to fine:

1. **Stack signatures** — the Docker-level fingerprint (base image → CUDA major·
   minor, Python minor, torch pin) for all 38 services.
2. **Package-level co-installability** — a direct pairwise comparison of every
   service's Python environment (both *frozen* image envs and *declared* upstream
   constraints). This is the headline evidence.

(The **footprint** sub-analysis — per-image size vs the bioq client — has been
moved to its own folder, `../footprint/`, and feeds Figure S3 panel b.)

## Protocol

### Part A — Stack fingerprints (coarse incompatibility)

For each `services/<name>-server/`, record the resolved stack signature from the
`Dockerfile` (base image → CUDA major.minor + devel/runtime) and the
`Dockerfile` / `pyproject.toml` (`python`, `torch`/`torchvision`, core ML
framework pin). The extracted table is committed as
`../footprint/data/signatures.csv` (one row per service, verbatim pins, with
provenance + hand-verified overrides noted per row).

### Part B — Package-level co-installability (fine; the headline)

For every service, extract its Python dependency set, then ask: *can two services
share one venv?*

- **Frozen view** (`data/service_dependency/<svc>.txt`): the fully
  resolved, fully pinned environment inside each built image (`name==version`).
  Comparing these answers "can the two frozen envs share one venv exactly as-is?"
- **Declared view** (`data/repo_dependency/<svc>.txt`): the upstream
  tool's own constraints from `pyproject.toml` / `setup.py|c` /
  `requirements*.txt` / conda env files. Comparing these answers "does a single
  version exist that satisfies both tools' declared requirements?"

Both views feed `analyze_compat.py`, which grades every shared-package version
difference by severity (HARD vs SOFT) and reports pairwise conflict matrices plus
per-package fragmentation (see **Method**).

## Method — package-level co-installability (as implemented)

`analyze_compat.py` compares every pair of services' package sets. Two
definitions are reported for every pair:

- **co-installable (strict):** the two envs can share one venv *exactly as-is* —
  every shared package is pinned identically. Any shared-package difference fails
  this (only one version of a package can be installed).
- **reconcilable (graded):** a *single* version could satisfy both, were we free to
  bump pins. Each shared-package version difference is graded:
  - **HARD** = irreconcilable — differing **major** (or 0.x minor) version, a
    differing **CUDA/local build tag** (`+cuXXX`), or (declared view) **disjoint**
    specifier ranges: no single version satisfies both.
  - **SOFT** = reconcilable by a coordinated bump — **minor** / **patch** difference
    (frozen view) or **overlapping-but-different** ranges (declared view).

A pair is **HARD-incompatible** iff at least one shared package is HARD. The frozen
view is the firmest statement: any conflict the methods *can* detect is already
materialised as a concrete pin, so HARD is a genuine lower bound on real
incompatibility; SOFT there is a "likely reconcilable" estimate, not a proof. The
declared view is the resolver-accurate statement: with `packaging.SpecifierSet`
intersection, a shared package is HARD iff *no* version satisfies both declared
constraints.

**Why not a resolver (uv) as the primary tool?** Two exact `==` pins at different
versions can only be *confirmed*, not negotiated, so on frozen inputs uv's best case
merely reproduces the set verdict — slower and needing network. Worse, these envs
contain packages not on the public index (the private `bioagent-service-framework`,
CUDA-local `torch==…+cuXXX`, conda-only scientific packages): uv reports those as
"not found" and fails resolution, conflating *unavailability* with
*incompatibility*. The set method has neither problem. `--uv-verify` runs uv on a
sample purely to demonstrate uv agrees with the set method on every pair it can
judge.

## Metrics

- **% service pairs HARD-incompatible** (cannot share one venv even after a bump) —
  the headline number. Frozen envs: **91.8 %**; declared constraints: **48.6 %**.
- **% service pairs that cannot share one venv as-is** (any shared-pin difference).
  Frozen: **96.8 %**; declared: **90.1 %**.
- **Distinct resolved versions** of core libraries, e.g. torch **17 builds** in the
  frozen envs, numpy **12** — the "fragmented zoo" made quantitative.
- **Stack fingerprint spread:** 15 distinct torch pins (1.12 → 2.12), CUDA 11/12,
  four CUDA minors, four Python minors, 23 distinct signatures.

## Results (regenerated from the current repo)

### Stack fingerprints (`../footprint/data/signatures.csv`, 38 services)

| Metric | Value |
|---|---|
| Services audited | **38** |
| Distinct torch pins (Dockerfile level) | **15**, spanning **torch 1.12 → 2.12** |
| CUDA majors | **12 (×22)**, **11 (×7)** — plus **9** non-CUDA base images |
| CUDA minors in use | 11.8, 12.1, 12.2, 12.4 |
| Python minors in use | 3.9, 3.10, 3.11, 3.12 |
| Distinct stack signatures (python × torch × CUDA-major) | **23** |

### Package-level co-installability

| View | Services | Pairs | HARD-incompatible | any pin diff (can't share as-is) | fully compatible |
|---|---|---|---|---|---|
| **Frozen envs** (image) | 34 | 561 | **515 (91.8 %)** | 543 (96.8 %) | 18 (3.2 %) |
| **Declared deps** (repo) | 32 | 496 | 241 (48.6 %) | 447 (90.1 %) | 49 (9.9 %) |

- *Frozen view = the firm lower bound:* 91.8 % of image pairs carry a HARD
  (major / CUDA-build) pin clash. 96.8 % cannot share a venv as-is. Only 18 pairs
  (3.2 %) have identical shared pins.
- *Declared view = the resolver answer:* 90.1 % of tool pairs have some constraint
  difference; 48.6 % have disjoint ranges — no single version can satisfy both.
- **Coverage is complementary and jointly complete:** the frozen view covers the 34
  images built on this host; the declared view covers 32 tools with parseable
  upstream files; together they span all 38 services (the 4 GPU images not built —
  haddock3, lasermpnn, odesign, turbohopp — are covered by the declared view; the 6
  with no/empty declared files are covered by the frozen view).

**Top conflict-driving packages** (frozen view — `package` / distinct versions /
conflicting pairs):

| Package | Versions | Conflicting pairs |
|---|---|---|
| numpy | 12 | 375 |
| scipy | 10 | 310 |
| setuptools | 7 | 285 |
| **torch** | **17** | 269 |
| rpds-py | 3 | 269 |
| typing_extensions | 2 | 240 |
| tqdm | 8 | 232 |
| charset-normalizer | 4 | 227 |
| networkx | 6 | 216 |
| pandas | 11 | 212 |

(Declared view drives the same story: numpy ×24 versions → 323 pairs, pandas ×16 →
257, scipy ×14 → 165, rdkit ×13 → 145, torch ×14 → 91.)

### Headline for the paper

> The 38-tool fleet spans **15 torch pins across torch 1.12→2.12** (CUDA 11 and 12,
> four CUDA minors, four Python minors, 23 stack fingerprints). At the package
> level, **91.8 % of frozen-image pairs are HARD-incompatible** — they pin
> irreconcilable torch/CUDA builds or major-versioned core libraries, so they cannot
> share a single venv even after a coordinated bump (96.8 % cannot share one as-is).
> bioq replaces all of it with a thin client whose only direct runtime dependency is
> `httpx` (see the footprint analysis for the measured size contrast).

## Outputs

The three package-level figures are rendered once per view, in parallel dirs:
**frozen** under `figures/frozen/`, **declared** under
`figures/declared/`. In each dir:

- **compat heatmap** (`E1_compat_heatmap.pdf`) — services × services matrix of
  HARD-conflict counts (white → amber → red).
- **co-install heatmap** (`E1_coinstall_heatmap.pdf`) — binary "can two services
  share one venv?" matrix (green = compatible, grey = not).
- **package fragmentation** (`E1_package_fragmentation.pdf`) — top conflict-driving
  packages (horizontal bars, `#versions` in the label).

The **footprint figure** now lives in `../footprint/figures/` (log-scale image
sizes vs the bioq client).

## How to run

All numbers regenerate from the committed scripts. `docker` is needed for the
frozen-env extraction. The stack signatures (`../footprint/data/signatures.csv`)
are committed input (see **Threats**).

### Package-level dependency analysis (Part B)

**Frozen envs** (from built images; requires `docker` + the built images):

```bash
python3 extract_deps.py                              # local tags
python3 extract_deps.py --registry harbor.ruosheng.bio/aliyun_fc
# -> data/service_dependency/<svc>.txt  (pip-freeze, name==version)
```

**Declared deps** (from opensource git checkouts; stdlib only, no docker):

```bash
python3 extract_repo_deps.py <name> <repo_dir> <output_file>

# single repo, e.g.
python3 extract_repo_deps.py boltz opensource/boltz \
    data/repo_dependency/boltz.txt

# bulk regeneration (all repos in the manifest)
while IFS=, read -r svc repo status npkgs srcs err; do
  [ "$svc" = service ] && continue; [ -z "$repo" ] && continue
  python3 extract_repo_deps.py "$svc" \
      "opensource/$(basename "$repo")" \
      "data/repo_dependency/$svc.txt"
done < data/repo_manifest.csv
```

**One-shot run (analysis + figures for both views):**

```bash
./run.sh
# -> data/frozen/ + figures/frozen/     (frozen view)
# -> data/declared/ + figures/declared/ (declared view)
```

Or run the two views explicitly:

```bash
# frozen view (image envs): data/service_dependency -> data/frozen/
python3 analyze_compat.py \
    --dep-dir data/service_dependency --out-dir data/frozen

# declared view (repo constraints): data/repo_dependency -> data/declared/
python3 analyze_compat.py \
    --dep-dir data/repo_dependency --out-dir data/declared

# optional resolver cross-check (needs network)
python3 analyze_compat.py --uv-verify
```

Each view emits `pairwise_compat.csv`, `conflict_matrix.csv`,
`package_fragmentation.csv` into its `--out-dir`. The frozen view is stdlib-only;
the declared view additionally needs `packaging` (`uv run --with packaging python …`).

**Figures:**

```bash
python3 plot_compat.py                              # frozen -> figures/frozen/
python3 plot_compat.py --data-dir data/declared \
    --out-dir figures/declared                     # declared view
# requires matplotlib, pandas, numpy
```

## Files

### Package-level dependency analysis

- `extract_deps.py` — extract the fully-resolved pip dependency set per service from
  its built Docker image (`importlib.metadata` inside the container). Outputs
  `data/service_dependency/<svc>.txt` (and an extraction manifest).
- `extract_repo_deps.py` — extract declared dependencies from one opensource git
  checkout. Positional: `name`, `repo_dir`, `output_file`. Scans pyproject.toml /
  setup.py|c / requirements*.txt / conda *env*.yml|yaml, AND-joins constraints per
  package, strips conda build hashes. Output is requirements-style text with a `#`
  provenance header. Stdlib only; no docker.
- `analyze_compat.py` — pairwise co-installability analysis (see **Method**).
  Compares each pair's package sets, grades version differences HARD/SOFT, and
  writes `pairwise_compat.csv`, `conflict_matrix.csv`, `package_fragmentation.csv`.
  Frozen view = direct pin comparison; declared view = `packaging.SpecifierSet`
  intersection.
- `plot_compat.py` — offline render of the three PDF figures from the CSVs.
- `run.sh` — one-shot regenerates analysis + figures for **both** views into the
  per-view dirs below.
- `data/service_dependency/` — per-service frozen-env files (`name==version`) —
  **input** to the frozen view.
- `data/repo_dependency/` — per-service declared-dependency files — **input** to the
  declared view.
- `data/repo_manifest.csv` — service → repo mapping and extraction status/counts.
- `data/frozen/` — frozen-view analysis outputs (default `--out-dir`).
- `data/declared/` — declared-view analysis outputs.
- `figures/frozen/` — frozen-view figures: `E1_compat_heatmap.pdf`,
  `E1_coinstall_heatmap.pdf`, `E1_package_fragmentation.pdf`.
- `figures/declared/` — declared-view figures (same three names).

The **stack-signature table** (Part A) is committed at
`../footprint/data/signatures.csv`; the **footprint** sub-analysis (former Part C)
lives in `../footprint/` with its own README.

## Data to record

All artifacts are regenerable from the committed scripts. Key outputs:
`../footprint/data/signatures.csv` (per-service pins),
`data/service_dependency/<svc>.txt` (frozen inputs),
`data/repo_dependency/<svc>.txt` (declared inputs), and
`pairwise_compat.csv` / `conflict_matrix.csv` / `package_fragmentation.csv` per view
(`data/frozen/` and `data/declared/`), with figures under
`figures/frozen/` and `figures/declared/`.

## Threats to validity & honest caveats (state in the paper)

- **Pins are recorded verbatim** (`../footprint/data/signatures.csv` and the
  per-service dependency files carry provenance), so the conflicts are auditable,
  not asserted.
- **Hard vs soft conflicts.** Only HARD conflicts (major / CUDA-build / disjoint
  ranges) are irreconcilable; SOFT ones (minor/patch / overlapping ranges) are
  excluded from the headline. In the frozen view SOFT is an *estimate* of
  reconcilability (a frozen `==` pin hides the true allowable range), while HARD is
  a firm lower bound.
- **The frozen and declared views answer different questions** and cover different
  service subsets (34 vs 32 of 38). Report which view a number comes from; do not
  conflate the 96.8 % "cannot share as-is" (frozen) with the 48.6 % "disjoint ranges"
  (declared).
- **The shared `bioagent-service-framework` + `httpx`/`httpx-sse`** are pinned
  identically across the fleet (the one part of the stacks that *is* uniform), so
  they never drive a conflict; the conflicts come from the *scientific* layer
  (torch / numpy / scipy / rdkit / pandas / …), which is the point.
- **The signature-level "minimum #environments" script has not yet been ported into
  this tree.** `../footprint/data/signatures.csv` (the input fingerprint) is
  committed and reproduces the fingerprint facts (23 signatures, 15 torch pins,
  CUDA 11/12 split), but the clique-cover/environment-count step that previously
  produced the "≥14 environments" figure is superseded here by the direct
  package-level analysis; the paper's headline should be re-anchored to the
  package-level numbers above (or the signature script restored) before submission.