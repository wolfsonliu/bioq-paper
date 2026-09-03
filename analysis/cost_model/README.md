# Cost model: scale-to-zero vs owned GPU

**Role:** economics. **Feasibility:** per-job durations measured live; pricing from
the public FC rate card; the comparison is a transparent model.

This experiment compares bioq's per-job serverless (FC GPU) model against
owning/renting a dedicated GPU, parameterized by **duty cycle** d = the fraction
of wall-clock the GPU is actually computing. It is both the experiment design and
the implementation reference for this directory's scripts below.

## Claim

For the **bursty** usage typical of a wet-lab or small computational group, bioq's
per-job serverless model costs **less** than owning (or renting a persistent) GPU.
There is a duty-cycle **crossover** below which serverless always wins.

## Rationale

The audience (GPU-poor labs) cares about $ as much as convenience. The honest
result is not "serverless is always cheaper" but "here is the utilization at which
it flips" — which is exactly the decision input a lab needs. Framed against the
**compute barrier**, the cost model answers the question a lab actually asks — "do I need to
buy a GPU at all?" — and for bursty, occasional use the answer is no.

## Protocol

1. **Measure** per-job GPU-seconds for a representative service per discovery
   stage (reuse the throughput-scaling analysis's measured timing via `--throughput-data` where available); record the GPU class
   per service.
2. **$/job** = (GPU-seconds + cold-start) × the effective CU-derived $/GPU-s. FC
   has no flat per-GPU-second rate (see [Pricing assumptions](#pricing-assumptions)): `CU/s = vRAM_GB × series_coef`, charged on a
   tiered yuan/CU ladder and converted to USD at a stated assumed rate.
3. **Dedicated alternative**: amortized purchase = price/(lifetime×12), or a
   persistent cloud GPU VM $/hour × 730.5 h/mo — a fixed $/month independent of use.
4. **Duty cycle**: serverless monthly cost = max_jobs(d=1) × d × wavg_$/job; solve
   for the **break-even d*** where serverless cost = dedicated cost.
5. **Sensitivity**: sweep FC GPU price ±30 % and 3 job-mix scenarios; report a
   band, not a point.

## Metrics

- $/job per representative service.
- $/month vs duty cycle for both models.
- **Break-even utilization** d* (the crossover).

## Pricing assumptions

FC GPU pricing is **CU-billed**, per the sheet in
[`aliyun_fc_price.md`](./aliyun_fc_price.md) (snapshot 2026-08-24). There is no
single per-GPU-second rate; instead GPU usage converts to **CU** and is priced on
a tiered ladder:

- CU ladder (yuan/CU): tier 1 `(0, 1e8]` → **0.00012**; tier 2 `(1e8, 5e8]` →
  0.00010; tier 3 `>5e8` → 0.00008. A bursty lab stays far inside tier 1, so the
  model uses **tier 1**.
- GPU conversion: `CU/s = vRAM_GB × series_coef`, with active-state series
  coefficients `Tesla 2.1`, `Ampere 1.8`, `Hopper 2.31` CU/(GB·s).

Currency is unified to USD at an **assumed** rate **1 USD = 6.80 CNY**
(edit `CNY_PER_USD` in `config.py`; the source sheet is in CNY).

| GPU class | series | vRAM | CU/s | ¥/GPU-s | $/GPU-s | ≈$/hr | Purchase $ | Lifetime | Cloud VM $/hr |
|-----------|--------|------|----------|-----------|-----------|-------|-----------|----------|---------------|
| T4 | Tesla | 16 GB | 33.6 | ¥0.004032 | $0.000593 | $2.13 | $3,000 | 4 yr | $0.60 |
| A10 | Ampere | 24 GB | 43.2 | ¥0.005184 | $0.000762 | $2.74 | $5,000 | 4 yr | $0.90 |
| A100 | Ampere | 40 GB | 72.0 | ¥0.008640 | $0.001271 | $4.57 | $15,000 | 4 yr | $2.50 |
| H100 | Hopper | 80 GB | 184.8 | ¥0.022176 | $0.003261 | $11.74 | $30,000 | 4 yr | $5.00 |

Cold-start overhead: 10 s per invocation (conservative mean).

## Controls / threats to validity

- **State all pricing assumptions and dates explicitly.** Pricing changes; present
  this as a reproducible model with inputs, not a fixed claim (the CU ladder,
  series coefficients, vRAM sizes, and CNY→USD rate are in
  [Pricing assumptions](#pricing-assumptions)).
- **Include realistic serverless overheads** (cold-start billed time, storage,
  egress) so the comparison is not rigged in bioq's favour.
- **vRAM is a modelling input** — the source sheet gives CU/(GB·s) but not the
  instance vRAM; sizes above are `config.py`'s single source of truth (A100 = 40 GB).
- **Non-GPU CU resources** (vCPU, memory, disk, invocations) also bill as CU but
  are not separately priced in the source sheet, so only GPU CU is counted — the
  serverless line is a floor.
- **Shallow-sleep idle billing** (浅休眠) — keeping a warm idle instance bills a
  reduced CU rate (0.2–0.5 CU/(GB·s)); bioq releases instances (scale-to-zero),
  so the active-only line is the relevant cost floor, but keep-warm deployments
  pay this idle rate and must not be conflated with scale-to-zero.
- **Above d*, a dedicated GPU wins** — do not overclaim.

## How to run

```bash
./run_all.sh          # mock → model → plot
```

Individual steps:
```bash
python3 make_mock.py                               # -> data/mock_single_job_stats.json
python3 model.py                                   # -> data/cost_table.csv, break_even.json, sensitivity.json
uv run --with matplotlib,numpy python3 plot.py     # -> figures/E4_cost_curve.pdf
```

To use the throughput-scaling analysis's measured timing data:
```bash
python3 model.py --throughput-data ../throughput_scaling/data/single_job_stats.json
```

## Files

| File | Role |
|------|------|
| `config.py` | Single source of truth: CU pricing, exchange rate, service catalog, job mix defaults |
| `model.py` | Core cost model: $/job, break-even duty cycle d*, sensitivity sweep |
| `plot.py` | the cost model figure (cost–duty-cycle curve) |
| `make_mock.py` | Fabricate mock GPU-seconds data for offline testing (no measured timing data needed) |
| `run_all.sh` | Offline orchestrator (mock → model → plot) |
| `data/` | `cost_table.csv` (the cost table), `break_even.json`, `sensitivity.json`, `mock_single_job_stats.json` |
| `figures/` | `E4_cost_curve.pdf` |

## Outputs

- **Cost model figure** — cost vs duty-cycle break-even curve (flat dedicated line crossed by
  the linear pay-per-use line), with the crossover d* marked and a sensitivity
  band → `figures/E4_cost_curve.pdf`.
- **Cost table** — $/job per representative service + GPU class →
  `data/cost_table.csv` (CSV, no figure PDF).
- `data/break_even.json` — break-even d* for each GPU class + weighted mix.
- `data/sensitivity.json` — d* across GPU price ±X% and job-mix scenarios.

## Self-test (no cloud)

```bash
./run_all.sh
```

## Results (measured timing from the throughput-scaling analysis injected via `--throughput-data`; regenerated 2026-08-25)

4 of 10 services use measured single-job times from the throughput-scaling
analysis (proteinmpnn 28 s, rfdiffusion2 13 s, reinvent 30 s, dockq 13 s); the 6
heavier services that analysis did not measure keep their config defaults (boltz
600 s, diffdock 480 s, flowmol 300 s, esmfold2 180 s, alphafold 900 s, genie3 60 s).

| Metric | Value |
|--------|-------|
| Weighted-average $/job (A100 mix) | ~$0.18 |
| Break-even d* (A100, amortized) | ~8.8 % duty cycle |
| Break-even d* (A100, cloud VM) | ~52 % duty cycle |
| Break-even d* (T4, amortized / cloud VM) | ~3.6 % / ~25 % |
| Break-even d* (A10, amortized / cloud VM) | ~5.0 % / ~31 % |
| Max jobs/mo @ 100 % duty cycle (A100 mix) | ~19,600 |

**Two honesty flags before printing:**
- `rfdiffusion2` measured 13.5 s in the throughput-scaling analysis, far below
  its ~5–10 min design expectation — treat its ~$0.03/job as non-representative
  until the throughput-scaling input is confirmed (likely a trivial/degenerate
  contig).
- The cost model adds a 10 s cold-start on top of the throughput-scaling
  analysis's wall-clock single-job times (which already include scheduling),
  slightly over-billing fast jobs.

## Data to record

Measured per-job GPU-seconds per service, the rate card snapshot (with date),
and the sensitivity-sweep inputs are recorded in this directory's `data/`
folder. Raw experiment outputs also live under `data/` (`cost_table.csv`,
`break_even.json`, `sensitivity.json`).

---

## Extension: measured burst trace (scale-to-zero elasticity)

The main analysis models the duty-cycle crossover; this extension makes it
*observable* by tracing a realistic bursty day and reading the scale-to-zero
behavior off the trace.

### Protocol
1. Record a wall-clock trace of a bursty workload over a day: idle → burst of N
   jobs → idle → small burst → idle, sampling per-minute active instances + cost.
2. Plot per-minute cost through the trace, marking the return to $0 after each
   burst (scale-to-zero).
3. Overlay the dedicated-GPU flat line from the main cost model for the same day.

### Metrics
- Time to scale back to zero after a burst.
- Total $ for the traced day vs a fixed dedicated GPU's day-rate.

### Outputs
- **Burst-trace figure:** cost-per-minute trace with the scale-to-zero drops annotated.

### Data
This directory's `data/` folder (e.g. a `trace/` subfolder): trace log (timestamp, active instances, $/min) + plot script.