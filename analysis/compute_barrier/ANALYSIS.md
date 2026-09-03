# Compute barrier: analysis

This document is the *interpretation* of the compute-barrier analysis's results. It complements the
experiment spec and point numbers in [`README.md`](./README.md) (read that first
for protocol, metrics, and schema) and goes a step further: it reads the
committed `data/vram.csv` for what the numbers actually mean, separates what is
solidly established from what is only an upper bound, and lists exactly what
must be curated before any figure is printed in the paper.

All counts below were re-derived directly from `data/vram.csv` (39 rows) and
match the README's "Results" table.

---

## 1. What this experiment establishes

The compute barrier is **real, quantified, and separate from the
installation barrier**. The dependency-incompatibility analysis shows the fleet *cannot be installed in one place*
(dependency incompatibility). The compute-barrier analysis shows that, even if installation were free,
the fleet *cannot run on the hardware a lab actually owns*. These are two
independent, additive costs to the "just run it locally" baseline — and bioq
removes both at once by moving execution to serverless GPUs.

Concretely, from best-known values:

| statement | value |
|---|---|
| fleets services audited | **39** |
| services that are GPU-provisioned (have a `gpuConfig`) | **27** (69%) |
| GPU services with a usable VRAM number (`minimum` or `inferred`) | **26** |
| of those, unreachable on a laptop iGPU (0 GB discrete) | **26 / 26 (100%)** |
| of those, need **> 4 GB** (beyond entry consumer cards) | **24 / 26 (92%)** |
| of those, need **> 8 GB** (beyond a mainstream 8 GB card) | **14 / 26 (54%)** |
| of those, need **> 24 GB** (beyond a 24 GB workstation card) | **1 / 26 (4%)** |

The headline is the first two rows: **two-thirds of the fleet is GPU
deep-learning, and every one of those services needs a discrete GPU — no
laptop, however easy the install, can run the fleet.**

## 2. What the card-fit ladder looks like

Re-expressed as "what hardware could actually run this service" (cumulative,
best-known values, N = 26 GPU services):

| GPU | services that fit | share | unreachable |
|---|---|---|---|
| laptop iGPU (0 GB) | 0 | 0% | 26 (100%) |
| 4 GB consumer | 2 (`mmseqs2`, `proteinmpnn`) | 8% | 24 |
| 8 GB consumer | 12 | 46% | 14 |
| 24 GB workstation | 25 | 96% | 1 (`esmfold2`, 32 GB) |

Two observations matter more than the raw counts:

1. **The barrier is a step function, not a cost gradient.** The best-known
   values collapse into five levels — `{4, 8, 16, 24, 32}` GB — with the mode at
   **16 GB** (11 of 26) and the median at 16 GB. There is no smooth
   "you can buy a slightly better card" curve; the fleet sits at a handful of
   card classes. Two of the four "small" services (`mmseqs2` 4 GB,
   `proteinmpnn` 4 GB) are themselves CPU-capable and only optionally use a GPU,
   so the *true* GPU-deep-learning entry point is effectively **8 GB**.
2. **A 24 GB workstation card is almost enough, but not quite.** 25 of 26 fit —
   the single exception is `esmfold2` at 32 GB. This is precisely the referent
   the throughput-scaling and cost-model analyses need for "speedup vs a single workstation GPU": the owned-workstation
   baseline is a 24 GB card that can run everything *except* the largest
   embedding+diffusion service.

## 3. The methodology trap the data avoids (and one it doesn't)

### 3.1 Provisioned ≠ required — the flat 16 GB wall

The FC deployment provisions almost the whole fleet at one baseline card
(`fc.gpu.tesla.1`, 16 GB): **24 of 27 GPU-provisioned services (89%)** sit at
exactly 16 GB, with only `diffdock` (24), `esmfold2` (32) and `promera` (48)
above it. Had this experiment charted `fc_vram_gb` as the requirement, the
figure would collapse into a flat 16 GB line and the barrier would be
invisible. Keeping `fc_vram_gb` as an honesty column and plotting
`min_vram_gb` is the single most important design decision in this experiment,
and it is worth stating explicitly in any methods section.

### 3.2 Where the documented floors actually point

The 11 service with a **verbatim documented floor** (`kind = minimum`) tell a
cleaner story than the combined value:

| documented floor | # services |
|---|---|
| 8 GB | 8 |
| 16 GB | 3 (`openadmet`, `ppiflow`, `rfdiffusion2`) |

- Every verbatim floor is **≥ 8 GB**; none is below 4 GB. So even restricted to
  *documented* evidence, the laptop-therefore-barrier verdict holds.
- **No service has a documented floor above 16 GB.** The `> 24 GB` observation
  (`esmfold2`) and the two 24 GB values (`diffdock`, `promera`) are *all*
  `kind = inferred` (provisioned upper bounds / wrapper recommendations), not
  documented minimums. The "24 GB workstation can't run it" claim therefore
  currently rests on inference, not citation.

### 3.3 The one trap the data does not yet avoid

The 16 GB mode is **partly an artifact of provisioning**. Eight of the 11
values at 16 GB are `kind = inferred` and their `source` reads
"≤ provisioned 16 GB" — i.e., *we know we gave it 16 GB, not that it needs
16 GB*. A tool provisioned 16 GB but genuinely needing only 8 GB would still be
counted at 16 GB today. This biases the `> 8 GB` count **upward**: the true
number of services that cannot run on an 8 GB card is ≤ 14, and the documented
floors support only **3 of 11** above 8 GB. The direction of bias is
conservative for the paper's *headline* (the laptop claim is unaffected) but it
**overstates the specific 8 GB / 24 GB thresholds**, which is exactly where a
reviewer will probe.

## 4. Known data-quality issues (fix or state before printing)

These are flagged in the CSV but consolidate into four load-bearing caveats:

1. **Provenance split is 11 documented / 15 inferred / 1 tested.** Only 41% of
   the quantified GPU services carry a verbatim floor; 15/26 (58%) are
   low-confidence upper bounds; `lasermpnn` is `tested` only (the upstream
   documents the authors' *training* cards — "4× A6000" — with no inference
   floor extractable).
2. **`ensemble-server` has a spurious `gpuConfig`.** Its wrapper documents it as
   CPU-only ("ensemble-server 是 CPU 函数"), yet the deploy yaml provisions 16 GB.
   This single row produces the README's **27 vs 26** apparent inconsistency:
   27 services "have a gpuConfig", but only 26 are *actually GPU-running* (and
   the plot's `> 8 GB` provisioned count is 26). Worth a one-line note and,
   ideally, dropping that GPU slot.
3. **`lasermpnn` is a GPU model with no `gpuConfig`.** It lands in the
   "no-GPU" bucket (12) purely because it is unprovisioned and undocumented —
   not because it is CPU-only. So the "12 CPU-or-unprovisioned" bucket mixes
   genuinely CPU tools with one *mislabelled GPU* service. Any "12 of the fleet
   are CPU" sentence must be softened to "12 are not GPU-provisioned."
4. **`kind = cpu` is a heuristic, not a proof.** `collect_vram.py` assigns it
   when it finds *no* `gpuConfig` *and no GPU mention* in the docs. It is
   "no evidence of a GPU requirement," not "demonstrated CPU-only." The 11
   genuinely-CPU-looking tools (`dockq`, `diamond`, `seqkit`, `plip`,
   `haddock3`, `lightdock`, `bindflow`, `chembounce`, `turbohopp`, `odesign`,
   `qligfep`) are a minority and their classification is believable, but it has
   not been independently verified.

## 5. Coverage and provenance of the evidence corpus

- **39 fleet services** map 1:1 to upstream repos via the dependency-incompatibility analysis's
  `repo_manifest.csv` (39 rows), consistent with the paper's "38+ services"
  framing.
- `extract_docs.py` materialized a committed evidence corpus from the
  `opensource/` checkout: **57 repos → 134 doc files → 343 matched lines**
  (`data/upstream_docs/{index.csv,hits.tsv}`), each copied file sha256-pinned
  and each `source` quote carrying a `path:line` pointer in `vram.csv`. Every
  number in this experiment is therefore auditable back to a verbatim line —
  no fabricated figures.
- The **57 `opensource` repos exceed the 39 fleet services**: several are
  helper/client/alias repos (`proto-client`, `proto-language`, `proto-tools`,
  `la-proteina`, `proteina`, `MMseqs2-App`, `foundry`, …) or upstream projects
  not currently exposed as a fleet service. Notably, the corpus's single most
  extreme *documented* floor — **BindCraft "at least 32 GB"** — is **not** a
  deployed fleet service. If BindCraft is ever added to the fleet, it would
  immediately become the fleet's largest documented floor (32 GB), matching
  `esmfold2`'s inferred level.

## 6. Threats to validity (paper-grade statements)

- **"Minimum as documented/configured, not re-measured."** Values are floors
  read from READMEs and wrapper notes, or *upper-bound* provisioned capacities.
  None were re-measured by running the tool; do not imply otherwise.
- **Upper-bound bias on `> 8 GB` and `> 24 GB`.** See §3.3: those thresholds are
  inflated by `≤ provisioned 16 GB` inferences. The laptop claim (`> 0 GB`) is
  unaffected because it requires only that a discrete GPU is needed at all.
- **CPU services are real but a minority.** The barrier applies to the
  GPU-deep-learning *majority*, not to every service in the fleet — say so.
- **Thresholds are nominal card classes, not real-world headroom.** "8 GB" means
  an 8 GB card with nothing else resident; in practice usable VRAM is lower.
  This makes the barrier starker, but also means the chart is a *lower* bound on
  practical difficulty.
- **The figure's bars are provisioned, not required** (see §7).

## 7. Figure fidelity note

`plot.py` draws the **bar as `fc_vram_gb` (provisioned)** and overlays
`min_vram_gb` as amber markers (solid diamond = documented, hollow circle =
inferred); threshold lines at 4/8/24 GB carry per-threshold counts. The README's
"Outputs" sentence ("bar length = minimum VRAM") is **imprecise**: the bars are
provisioned, the minimum is the marker. This is cosmetic but the README line
should be corrected so the caption matches the figure.

## 8. What to curate before any number is printed in the paper

In priority order, matching the README's own staging note:

1. **Replace the 15 `inferred` rows with documented floors** wherever upstream
   states one (start with the heavyweights that drive the thresholds:
   `esmfold2`, `diffdock`, `promera`, `boltz`, `alphafold`, `iggm`,
   `megalodon`, `openbpmd`). Each must end `kind = minimum` with a
   `path:line` quote, or be dropped from the threshold counts.
2. **Resolve `lasermpnn`** — either find its inference floor or move it out of
   the "no-GPU" bucket explicitly.
3. **Resolve `ensemble-server`** — remove the spurious `gpuConfig` or document
   it as a known exception, so the 27/26 discrepancy disappears.
4. **Fix the README "Outputs" bar-vs-marker wording** (§7).
5. Only then quote the **> 8 GB** and **> 24 GB** figures; the **> 0 GB** and
   **> 4 GB** figures are already safe to state with the current data.

## 9. Bottom line for the paper

The compute-barrier analysis delivers the visual and quantitative complement to the dependency-incompatibility analysis's "can't install": a
per-service VRAM strip that shows **100% of the GPU fleet is unreachable from a
laptop** and **~54% needs more than a mainstream 8 GB consumer card** (best-known
values), against real hardware thresholds. The claim it supports — *the compute
barrier is separate from and additional to the incompatibility barrier, and bioq
removes it by moving to serverless GPUs* — is already well supported by the
documented floors alone. The *specific* 8 GB and 24 GB cut-points, however,
still lean on low-confidence upper bounds and must be curated before they are
printed as measured facts.