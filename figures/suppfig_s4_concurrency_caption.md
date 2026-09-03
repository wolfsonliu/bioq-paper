**Figure S4.** Throughput scaling of bioq serverless fan-out on Aliyun Function
Compute. Six representative services spanning three serverless tiers —
cold CPU (`dockq`, `plip`), hot GPU (`mmseqs2`, `proteinmpnn`), and warm GPU
(`reinvent`, `rfdiffusion2`) — are measured as a function of batch size
`N ∈ {1, 10, 50}`; the upper bound `N = 50` is the FC GPU instance-quota ceiling.
Each point is the mean over three independent replicates, with error bars showing
±1 standard deviation. Colour and marker identify the service (see the shared
legend beneath the panels).

- **(a) Makespan vs N** (log–log). Total wall-clock time to complete all `N` jobs,
  per service. A serial, single-worker baseline would grow proportionally to `N`.
- **(b) Speedup vs N** (log–log). Speedup relative to the serial baseline
  (`N × single-job time / bioq makespan`). The dotted grey line is the ideal
  `N×` (perfectly parallel) reference.
- **(c) Throughput vs N**. Completed jobs per hour, per service
  (`completed jobs / makespan`).
- **(d) Peak concurrency vs N**. Maximum number of simultaneous worker instances
  observed; the solid line is the replicate mean and the fainter dotted line is
  the per-replicate maximum. The dashed grey line is the ideal `c = N` reference
  (one instance per job).
- **(e) Per-job latency distribution** (log-scale box plots). Wall-clock latency
  per job (`t_completed − t_submit`), grouped on the x-axis by batch size `N`, with
  one coloured box per service; boxes pool all jobs across the three replicates.
- **(f) Cold-start overhead** (box plots). Time from submit to first `running`
  status per job, grouped by `N` and coloured per service. When the `running` status
  is not captured (the 5 s poll interval is too coarse for fast jobs), the full
  per-job latency is used as a conservative upper bound.