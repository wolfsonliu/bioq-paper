**Figure S5.** Per-job latency and cold-start overhead, grouped by
service, on Aliyun Function Compute. The x-axis lists six services; within each
service, three box plots show batch size N = 1, 10, 50 (lighter → darker). Boxes
pool all jobs across three replicates. Brackets show two-sided Mann–Whitney U
tests between adjacent N levels (`ns`, `*`, `**`, `***`, `****`).

- **(a) Per-job latency** (seconds, y-axis log scale). Wall-clock time per job,
  `t_completed − t_submit`.
- **(b) Cold-start overhead** (seconds). Time from submit to first `running` status;
  when `running` is not captured, the full per-job latency is used as a conservative
  upper bound.