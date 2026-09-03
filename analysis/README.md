# analysis

The six analyses that substantiate the figures/tables in
`latex/manuscript.tex` and `latex/supplementary.tex`, gathered here so each one
can be read and reproduced standalone. Each folder uses the descriptive analysis
name (the internal experiment-numbering prefix was dropped when these were
organized out of the monorepo `experiments/` tree).

| Folder | Paper artifact(s) |
|--------|-------------------|
| `contract_conformance/` | Figure S1 (fleet-wide contract conformance) |
| `dependency_incompatibility/` | Figure S2 (dependency co-installability + conflict heatmap) |
| `compute_barrier/` | Figure S3 (per-service GPU VRAM barrier) |
| `footprint/` | storage-footprint half of Figure S3 (image size vs bioq client) |
| `throughput_scaling/` | Figures S4, S5 (serverless fan-out scaling) |
| `cost_model/` | Figure S6 (cost break-even) |
| `end_to_end_campaign/` | Figures S7, S8, S9; Table S2 (RFantibody de novo antibody campaign) |

## Provenance

These are copies of the corresponding private `experiments/` folders, with
bytecode caches (`__pycache__/`, `*.pyc`) and editor backup files (`~`) removed.
Working notes to keep in mind:

- `compute_barrier/opensource` is a symlink to a local bioagent checkout; re-point
  it if this tree moves to a machine without that checkout.
- `cost_model/` reads `throughput_scaling/data/single_job_stats.json` for its
  measured per-job timings — a cross-folder dependency among these analyses.
- `footprint/data/signatures.csv` (the stack-signature table) is shared input:
  `dependency_incompatibility/` reads it for its coarse-incompatibility evidence
  (Part A), and `footprint/` reads it as the service list for image sizing.

Not copied here: experiments the current manuscript/supplementary does not yet
cite with a figure or table (e.g. the transport-parity and agent-drivability
analyses, and the follow-up analyses). Add them when the manuscript acquires the
corresponding result.
