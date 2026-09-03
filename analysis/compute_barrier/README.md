# Compute-barrier quantification (VRAM chart)

**Role:** access headline — the compute barrier. **Feasibility:** computable NOW
(static values; no cloud, no GPU). **Status:** implemented — evidence corpus,
`data/vram.csv` (11 documented minimums + 15 inferred estimates covering all 27
GPU services), and the compute-barrier figure all produced (2026-08-24). Estimates are
`confidence=low` upper bounds — curate `data/minima_curated.csv` before printing.

## Claim

A large fraction of the fleet cannot run on a laptop or a typical lab
workstation at all, *independent of installation effort*: the compute barrier is
separate from, and additional to, incompatibility. bioq removes it by moving
execution to serverless GPUs.

## Rationale

The outline insists the compute barrier be named *separately* from the
incompatibility barrier, but until now it has only been asserted ("tens of GB").
A per-service VRAM plot against real hardware thresholds makes the barrier
visceral, and gives the throughput-scaling and cost-model analyses' "speedup vs a single workstation GPU" baseline a
concrete referent. It is the visual complement to the dependency-incompatibility analysis's "can't install": that analysis shows
the fleet *can't be installed* in one place; the compute-barrier analysis shows it *can't run* on the
hardware a lab actually owns.

## Protocol

1. Per service, record the **minimum GPU VRAM** the tool needs to run, from the
   upstream `README.md` (browsable via the `./opensource/` symlink) or the
   paper's Methods. Record the **FC-provisioned** capacity as a separate column
   (see *Data source* — it is a platform allocation, not the tool's minimum).
2. Define hardware thresholds: laptop iGPU (**0 GB** discrete VRAM), **4 GB**
   consumer card, **8 GB** consumer card, **24 GB** workstation card.
3. For each threshold, count how many services require more, and produce a
   services-vs-VRAM figure: per-service sorted horizontal bars (length = minimum
   VRAM) with the threshold lines drawn and the count above each line annotated.

## Metrics

- #services requiring **> 4 GB / > 8 GB / > 24 GB** VRAM.
- Fraction of the fleet unreachable on a laptop (minimum VRAM **> 0 GB**) and on
  a 24 GB workstation (**> 24 GB**).

## Data source

Two distinct values per service, kept in separate columns — conflating them is
the main correctness trap of this experiment:

| column | meaning | source |
|---|---|---|
| `min_vram_gb` | the tool's **documented minimum** — the value the barrier is about | upstream `README.md` (via `./opensource/<repo>/`) or the paper's Methods; hand-curated, not re-measured |
| `fc_vram_gb` | what the FC deployment **provisions** (an upper bound) | `bioq-services/services/<svc>-server/deploy/fc*.yaml` → `gpuConfig.gpuMemorySize` (MB) + `gpuConfig.gpuType` |

`./opensource/` is a symlink (`opensource -> <bioagent>/opensource`) to the
local bioagent `opensource/` checkout, so the upstream READMEs are browsable
from this directory; re-point the symlink if this folder moves. A
bioq-services service `README.md` is only a sparse fallback (few state a
minimum).

Upstream READMEs do **not** uniformly state a minimum, so each `min_vram_gb` row
records **how** the number was obtained (`kind`) and its verbatim evidence
(`source`), not a bare number:

- `kind = minimum` — an explicit documented floor ("at least N GB"; e.g.
  BindCraft "at least 32 Gb", or the wrapper "T4 8 GB 起步").
- `kind = inferred` — an **estimate**, not a documented floor: the best
  "runs-within" figure available (the FC-provisioned VRAM — an upper bound — or
  a wrapper "fits N GB" note, or a small allocation for a lightweight/CPU-capable
  tool). `confidence=low`; never reported as a measured minimum.
- `kind = tested` — only a card the authors *tested on* was found (e.g.
  RFdiffusion "1× A100 80 GB"); no number extractable as a floor → `min_vram_gb`
  blank.
- `kind = unverified` — no GPU requirement found in any doc.
- `kind = cpu` — no `gpuConfig` and no GPU requirement found in the docs
  (CPU-only service); sits outside the compute-barrier count.

`minimum` and `inferred` both carry a numeric `min_vram_gb` and feed the figure
(hollow marker = inferred estimate; solid = documented minimum). The other kinds
are kept in the CSV for provenance but are not charted.

CSV schema (one row per service):

```
service, gpu_class, fc_vram_gb, min_vram_gb, kind, source, confidence
```

`source` is a `path: "verbatim quote"` so every number is auditable (repo rule:
never fabricate; cite "documented", not "measured").

The provisioned value is **not** a usable proxy for the minimum: the FC fleet
provisions almost every GPU service at the same baseline card
(`fc.gpu.tesla.1`, 16 GB), so `fc_vram_gb` alone collapses the chart into a flat
16 GB line. Plot `min_vram_gb`; keep `fc_vram_gb` as an honesty column so the
figure also shows "what we actually provision vs what the tool needs". Units:
the yaml `gpuMemorySize` is in **MB** (16 384 = 16 GB); divide by 1024 for GiB.

The VRAM column was planned for the footprint analysis's table
(`{CUDA, python, torch, image GB, #pkgs, min VRAM}`) but has **not yet been
collected there** (the footprint analysis covers image sizes only), so the compute-barrier analysis collects it
directly rather than reusing a table that does not exist yet.

Services with no `gpuConfig` block (≈12 of the `*-server` services —
CPU-only or not GPU-provisioned, e.g. `dockq`, `diamond`, `seqkit`, `plip`,
`chembounce`) sit outside the compute-barrier count.

## Controls / threats to validity

- Cite VRAM as "minimum as documented/configured", not re-measured — do not
  overclaim precision.
- Keep **provisioned** (`fc_vram_gb`) and **required** (`min_vram_gb`) separate.
  Using the provisioned value as the minimum would inflate the barrier: a tool
  that genuinely needs 8 GB may be provisioned 16 GB and wrongly counted as
  unreachable on an 8 GB card. Prefer the upstream minimum where one exists.
- Note that CPU services exist but are a minority; the barrier applies to the
  GPU-deep-learning majority, not to every service in the fleet.

## Results (regenerated 2026-08-24)

| metric | value |
|---|---|
| services audited | **39** |
| GPU-provisioned / CPU-or-unprovisioned | **27 / 12** |
| documented minimum (`kind = minimum`) | **11** services |
| inferred estimate (`kind = inferred`, from `data/minima_curated.csv`) | **15** services |
| best-known VRAM > 4 GB / > 8 GB / > 24 GB | **24 / 14 / 1** |
| provisioned VRAM > 8 GB / > 24 GB | **26 / 2** — esmfold2 32 GB, promera 48 GB* |

\* promera is provisioned 48 GB (ada.1), but its wrapper documents "24 GB for
typical complexes" — the estimated minimum is 24 GB, not 48 GB.

The 11 minimums are verbatim floors (wrapper "T4 8 GB 起步 / 绰绰有余",
REINVENT4 "8 GiB … sufficient", openadmet "≥ 16 GB"). The 15 `inferred` rows are
**estimates, not measurements**: each is the best "runs-within" figure available
— the FC-provisioned VRAM (an upper bound) for memory-hungry models, or a small
allocation for CPU-capable/lightweight tools (ensemble 0, mmseqs2 4, proteinmpnn
4, deeprank-ab 8, immunebuilder 8). Every inferred row is `confidence=low` and
should be re-curated against a documented source before any number is printed in
the paper.

## How to run

```bash
# (1) materialize the resource-requirement evidence corpus — DONE, committed
uv run python extract_docs.py            # ./opensource -> data/upstream_docs/

# (2) collect provisioned GPU from bioq-services deploy yamls + the minimums
#     (verbatim quotes + kind from data/upstream_docs/) — DONE -> data/vram.csv
uv run python collect_vram.py            # stdlib only

# (3) plot sorted bars + threshold lines — DONE -> figures/
uv run --with matplotlib python plot.py
```

`extract_docs.py` walks `./opensource/` and copies each repo's `README*` plus
any `docs/` file matching a resource signal (GPU/VRAM/CUDA/card class/disk)
into `data/upstream_docs/<repo>/`, with `index.csv` (what was copied, why,
sha256) and `hits.tsv` (matched lines, for quote extraction). Re-run safe.

`collect_vram.py` merges four inputs, in priority order:

- `data/minima_curated.csv` — author-curated `min_vram_gb`/`kind`/`source`
  overrides (wins over everything else; 16 curated estimates committed).
- `data/upstream_docs/` (or `./opensource/` live) — upstream `README*`/`docs`
  files, grep'ed for an explicit floor (English + Chinese markers) and for
  tested/recommended cards.
- `bioq-services/services/<svc>-server/README.md` — the wrapper README, where
  most documented minimums actually live (e.g. "T4 8 GB 起步").
- `bioq-services/services/<svc>-server/deploy/fc*.yaml` — `fc_vram_gb` /
  `gpu_class` from `gpuConfig.gpuMemorySize` (MB) + `gpuConfig.gpuType`.

## Layout

```
compute_barrier/
├── README.md        # this file (spec + how to run)
├── opensource/      # symlink → upstream checkout (upstream README source)
├── extract_docs.py  # materialize data/upstream_docs/ from ./opensource (DONE)
├── collect_vram.py  # provisioned VRAM from deploy yamls + curated minimums (DONE)
├── plot.py          # sorted horizontal bars vs min VRAM + threshold lines (DONE)
├── data/
│   ├── upstream_docs/   # evidence corpus: <repo>/README* + matched docs, index.csv, hits.tsv
│   ├── minima_curated.csv  # author-curated min_vram_gb/kind/source overrides
│   └── vram.csv         # {service, gpu_class, fc_vram_gb, min_vram_gb, kind, source, confidence}
└── figures/         # generated figure (fig-e13-vram.{png,pdf})
```

## Outputs

- **Compute-barrier figure:** per-service sorted horizontal bars (length = minimum VRAM) with
  hardware threshold lines at 0 / 4 / 8 / 24 GB and per-threshold counts of
  services that cannot run.

## Data

`data/upstream_docs/`: the committed evidence corpus — per-repo `README*` plus
any resource-relevant `docs/` file, with `index.csv` (copied files + sha256) and
`hits.tsv` (matched lines). `data/vram.csv`: per-service
`{service, gpu_class, fc_vram_gb, min_vram_gb, kind, source, confidence}`.
`data/minima_curated.csv`: the author-maintained minimum table (overrides; 16
curated estimates for the services with no documented floor).