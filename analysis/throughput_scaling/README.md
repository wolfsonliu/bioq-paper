# Throughput scaling on parallel workloads

**Role:** scale proof. **Feasibility:** needs live cloud (deployed FC fleet).

For embarrassingly-parallel screening/design workloads, bioq's serverless dispatch
delivers throughput that a single workstation GPU cannot, **with zero user-side
orchestration** (no queue, no scheduler, no parallel code). This document is both
the experiment design and the implementation reference for
this directory's scripts.

## Claim

For embarrassingly-parallel screening/design workloads, bioq's serverless dispatch
delivers throughput that a single workstation GPU cannot, **with zero user-side
orchestration** (no queue, no scheduler, no parallel code).

## Rationale

The democratization story is incomplete without showing bioq enables *scale a lab
laptop/workstation cannot reach*. Fan-out over scale-to-zero GPU functions is
exactly the regime where serverless shines; this quantifies it honestly, including
its limits (cold starts, concurrency caps). This experiment also quantifies the
**compute barrier** directly: the baseline is serial execution on a single worker
(the one-job-at-a-time hardware a typical lab has) against which serverless
fan-out is measured.

## Protocol

The panel spans three serverless tiers (hot/warm/cold, GPU and CPU) so the scaling
story is not cherry-picked from a single warm service; the full panel is in
[Services tested](#services-tested).

1. Pick a fast, `hot`-tier service where per-job time is short enough to expose
   scheduling overhead (e.g. proteinmpnn `design`, mmseqs2 `msa`), plus heavier
   warm-tier GPU services and fast CPU (`cold`-tier) services as further data
   points.
2. Build a batch of N independent jobs from a fixed input pool, for
   N ∈ {1, 10, 50} (the upper bound of 50 is the Aliyun FC GPU instance quota
   ceiling).
3. **bioq arm:** submit all N via `bioq submit` (async, varying seed), then poll to
   completion; record submission time, per-job start/finish, makespan, and peak
   concurrency (distinct worker instances).
4. **Serial baseline:** model a single worker running the same N jobs serially as
   N × single-job time, with single-job time measured from the N=1 FC run.
5. Repeat each point 3× to get variance; run a throwaway warm-up batch and a
   cooldown between replicates to separate warm-start from cold-start runs.

## Services tested

| Service | Tier | GPU/CPU | Per-job time | Input |
|---------|------|---------|-------------|-------|
| `proteinmpnn design` | Hot | GPU | ~1–3 min | `5L33.pdb` (monomer) |
| `mmseqs2 msa` | Hot | GPU | ~30–60 s | `sequence.fasta` (147 aa) |
| `rfdiffusion unconditional` | Warm | GPU | ~1–2 min | None (standalone) |
| `rfdiffusion2 custom` | Warm | GPU | ~5–10 min | None (de novo contigs) |
| `reinvent sampling` | Warm | GPU | ~30–60 s | None (standalone) |
| `boltz predict_structure` | Warm | GPU | ~3–5 min | None (inline sequences) |
| `boltzgen design` | Warm | GPU | ~3–5 min | `vanilla.yaml` |
| `alphafold fold` | Warm | GPU | ~5–10 min | `bench.fasta` (25 aa) |
| `plip profile` | Cold | CPU | ~5–15 s | `1vsn.pdb` (complex) |
| `dockq score` | Cold | CPU | ~2–5 s | `model.pdb` + `native.pdb` |

## Metrics

- **Makespan(N):** wall-clock to finish all N jobs.
- **Throughput (jobs/hour) vs N:** completed jobs / makespan.
- **Speedup vs serial:** `N × single-job time / bioq_makespan` (serial baseline).
- **Peak concurrency:** max simultaneous worker instances observed.
- **Per-job latency:** wall-clock time for a single job from submit to completion
  (`t_completed − t_submit`); decomposed into cold-start/queue-wait
  (`t_running − t_submit`) plus compute time (`t_completed − t_running`),
  reported per (service, N) as median/mean ± std over the 3×N pooled jobs.
- **Cold-start overhead:** time from submit to first `running` status. When
  `t_running` is unavailable (the 5 s poll interval is too coarse to catch the
  `running` status for fast-completing jobs), falls back to the full per-job
  latency `t_completed - t_submit` as a conservative upper bound — for fast jobs
  the cold start dominates the total latency.
- **Statistical significance** of the N-dependence of each metric (Kruskal-Wallis
  omnibus + Mann-Whitney U pairwise, non-parametric) — see
  [Statistical tests](#statistical-tests).

## Statistical tests (`analyze.py`)

For each service, every metric is compared across batch sizes N with
non-parametric tests (no normality assumption — appropriate for 3 replicates and
skewed/long-tailed latency data):

- **Omnibus:** Kruskal-Wallis H across all N levels (chi-square approximation,
  tie-corrected).
- **Pairwise:** two-sided Mann-Whitney U between each pair of N levels (exact
  permutation), with rank-biserial effect size `r` (1 − 2U/nₐn_b).

Two aggregation levels are reported: **replicate level** (n = 3 per N, matching
the reported means ± std) and **job level** (per-job cold-start and latency pooled
across replicates, n = 3×N — more power for per-job quantities). Replicate-level
pairwise p-values floor at 0.1 for n=3 vs n=3 (exact); the job-level tests carry
the signal for cold start. p-values are uncorrected for multiple comparisons.

**Presentation:** the full `statistical_tests.csv` is compressed into
`data/table_s2.{csv,md}` (medians per N + K-W omnibus + headline pairwise tests),
and the cold-start panel of `figures/E3_bioq_by_service.pdf` is annotated with
pairwise Mann-Whitney significance brackets between adjacent N levels
(ns \* \*\* \*\*\* \*\*\*\*) drawn by `plot_aliyun_by_service.py`.

## Controls / threats to validity

- Identical input set and container digest across arms.
- **Report FC concurrency limits and cold-start / GPU-contention stalls honestly** —
  resource contention can queue jobs (an observed real caveat); show it rather
  than hide it.
- Distinguish warm vs cold tiers; do not cherry-pick the warm curve.
- Present the full scaling curve, not a single speedup headline.

## How to run

Collection has to touch the deployed stack, so run it on the ECS host; analysis and
plotting are pure and run anywhere (with `uv` for scipy + matplotlib).

1. **Stage inputs**: `./fetch_inputs.sh`
2. **Collect bioq arm** (on ECS, with gateway access):
   ```bash
   export PATH="$HOME/.venv/bin:$PATH"
   export BIOQ_PROFILE=ecs
   python3 collect_bioq.py
   ```
   For each service × N ∈ {1, 10, 50} × 3 replicates:
   - Submit N jobs via `bioq submit` (async, varying seed)
   - Poll all to completion via `bioq status`
   - Record per-job timing (submit → running → completed) + peak concurrency
3. **Offline analysis** (anywhere):
   ```bash
   ./run_offline.sh
   ```
   Produces `data/throughput.csv`, `data/scaling_summary.json`,
   `data/single_job_stats.json`, `data/statistical_tests.{json,csv}`,
   `data/table_s2.{csv,md}`, `figures/E3_bioq.pdf`, `figures/E3_bioq_by_service.pdf`

## plot_aliyun.py — bioq-only standalone analysis

Unlike `analyze.py` (which computes the machine-readable `data/*.csv`/`*.json`
tables), this script reads raw results directly from `results/bioq/` and does its
own analysis. It discovers services, batch sizes, and replicates automatically —
no dependency on `config.py` or `analyze.py`.

```bash
python3 plot_aliyun.py
python3 plot_aliyun.py --results results/bioq --out figures/E3_bioq.pdf
```

Produces a single PDF with 6 panels:

| Panel | Content |
|-------|---------|
| (a) | Makespan vs N (log-log) |
| (b) | Speedup vs N (log-log), with ideal N× reference |
| (c) | Throughput (jobs/hour) vs N |
| (d) | Peak concurrency vs N |
| (e) | Per-job latency distribution (box plot by service and N) |
| (f) | Cold-start overhead: submit → running (box plot) |

## Files

| File | Role |
|------|------|
| `config.py` | Single source of truth: services, batch sizes, params, image tags |
| `fetch_inputs.sh` | Stage input files (copies from service test data) |
| `collect_bioq.py` | **ECS**: submit N async jobs via `bioq submit`, poll to completion, record timing |
| `analyze.py` | **Offline**: process FC timing logs into throughput/makespan/speedup-vs-serial tables |
| `plot_aliyun.py` | **Offline**: bioq-only (FC) standalone analysis + 6-panel PDF figure |
| `plot_aliyun_by_service.py` | **Offline**: bioq-only latency/cold-start box plots grouped by service |
| `make_mock.py` | Fabricate mock data for offline testing (no cloud required) |
| `run_offline.sh` | Offline orchestrator: analyze + plot |

## Outputs

- **Main figure (`figures/E3_bioq.pdf`)** — 6-panel figure from `plot_aliyun.py`:
  panels (a) makespan vs N and (b) speedup vs N realize the design's
  makespan-vs-N and speedup-vs-N panels (bioq sublinear/flat-ish makespan vs
  serial linear; speedup with the concurrency ceiling annotated), plus
  (c) throughput, (d) peak concurrency, (e) per-job latency, and (f) cold-start
  overhead.
- **Per-service figure (`figures/E3_bioq_by_service.pdf`)** — per-service
  latency/cold-start box plots; the cold-start panel carries pairwise Mann-Whitney
  significance brackets between adjacent N levels (stars for p<0.05, `ns`
  otherwise, from `plot_aliyun_by_service.py`).
- Machine-readable tables under `data/`:
  - `throughput.csv` — per-(svc, N, rep) throughput, makespan, speedup-vs-serial
  - `scaling_summary.json` — aggregated stats per (svc, N)
  - `single_job_stats.json` — per-service single-job timing stats (serial baseline)
  - `statistical_tests.{json,csv}` — omnibus (Kruskal-Wallis) + pairwise
    (Mann-Whitney U) tests of each metric across N, per service
  - `table_s2.{csv,md}` — condensed Table S2, ready to paste into the supplementary

## Self-test (no cloud)

```bash
python3 make_mock.py && ./run_offline.sh
```

## Data to record

This directory's `results/bioq/` (raw per-job timing), `data/` (derived tables +
statistical tests), and `figures/`: per-job timing logs
(submit/start/finish/instance id), the input pool manifest (`inputs/`), baseline
single-job times, and the plotting scripts.

---

## Extension: contention & queuing characterization

The main analysis names "GPU contention can queue jobs" as a caveat; this
extension *shows* it from the same collection, no new runs required. The
queue-wait quantity (start − submit) is the same submit → `running` latency
already captured as cold-start overhead in panel (f) of `figures/E3_bioq.pdf` and
by `plot_aliyun_by_service.py`.

### Protocol
1. From the collected per-job logs (submit/start/finish), compute queue-wait =
   start − submit and compute-time = finish − start per job.
2. Plot queue-wait vs compute as a function of N (or peak concurrency); annotate
   the FC concurrency cap and any scheduling tail.

### Metrics
- Queue-wait histogram; median/max queue-wait vs peak concurrency.
- Tail identification: the longest queue-wait jobs (→ stalls).

### Outputs
- **Extension figure:** queue-wait vs concurrency, with the cap annotated.

### Data
Reuses this directory's `data/`; adds only an analysis/plot script.