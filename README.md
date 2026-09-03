# bioq — reproducible manuscript repository

This repository is the reference companion to the bioq application note:

> **Liu, Z. & Wang, Y.** — *bioq: a unified, agent-native command-line interface
> to a fleet of AI drug-discovery tools.* 

**bioq** turns a fragmented ecosystem of GPU-hungry AI drug-discovery tools into
a single, self-describing command-line interface: any tool runs from a laptop
with no local models, CUDA, or cloud setup, and the same interface is equally
drivable by an autonomous coding agent to automate whole discovery workflows.
It is backed by **bioq-services** — a control-plane gateway plus a growing fleet
of **38+** containerized tools spanning **7 discovery stages** and **6 molecular
modalities**, dispatched to serverless GPUs and billed per job.

The software introduced in the paper lives in two separate repositories:

- **bioq** (client + CLI): <https://github.com/wolfsonliu/bioq>
- **bioq-services** (gateway + service fleet): <https://github.com/wolfsonliu/bioq-services>

## Repository layout

| Path | What it contains |
|------|------------------|
| `latex/` | Manuscript source (`manuscript.tex`) and supplementary material (`supplementary.tex`) built on the OUP authoring template; the bibliography; `build.sh` renders `manuscript.pdf` and `supplementary.pdf`. |
| `figures/` | Rendered display items — Figure 1 plus Figures S1–S9 as SVG/PDF with per-figure captions, and the CSV sources + notes behind Tables S1–S2. `FIGURES.md` is the number ↔ file ↔ analysis index. |
| `analysis/` | The self-contained analyses that generate each figure and table, one folder per analysis (see the mapping below). |

## Display items

Main text: **Figure 1** (architecture + fleet coverage) and **Table 1**
(operational benchmark). Supplementary material: **Figures S1–S9** and
**Tables S1–S2**. `figures/FIGURES.md` maps every display item to its generating
analysis and its inline citation site.

## Building the manuscript

```bash
cd latex
./build.sh          # → manuscript.pdf + supplementary.pdf
```

Requires a TeX Live installation (≥ 2020) with `pdflatex` and `bibtex`. The few
extra packages the OUP class needs (`totcount`, `algorithmicx`, `subfloat`,
`anyfontsize`) are vendored under `latex/texmf-local/` and are used only when the
local TeX Live does not provide them.

## Reproducing the figures and tables

Every quantitative display item traces to a script plus committed data under
`analysis/`. Each folder is standalone, offline-runnable, and documents its own
inputs, commands, and outputs in a local `README.md`.

| Display item | Analysis |
|--------------|----------|
| Figure S1 (contract conformance) | `analysis/contract_conformance/` |
| Figure S2 (dependency incompatibility) | `analysis/dependency_incompatibility/` |
| Figure S3 (compute + storage barrier) | `analysis/compute_barrier/`, `analysis/footprint/` |
| Figures S4–S5 (throughput scaling) | `analysis/throughput_scaling/` |
| Figure S6 (cost break-even) | `analysis/cost_model/` |
| Figures S7–S9, Table S2 (de novo antibody campaign) | `analysis/end_to_end_campaign/` |

## Citation

If you use bioq or build on this work, please cite the application note above. An
archived snapshot of this repository will be available on Zenodo (`<add DOI>`).

## License

The **bioq** and **bioq-services** software are open source under the MIT License
(see the repositories above). License terms for the manuscript text, figures, and
analysis code in this repository: `<add on release>`.

## Contact

<zhiheng.liu@pku.edu.cn>
