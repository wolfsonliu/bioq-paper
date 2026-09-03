# End-to-end cross-tool campaign (spec + code + case study)

**Role:** scientific payoff ("so what"). **Feasibility:** live cloud; leverages the
mature `pipelines/antibody_design` subdomain.

Runs a real discovery workflow **entirely through bioq** (no local GPU, a few
commands) that reproduces a *published* computational pipeline and recovers
comparable in-silico metrics — the scientific "so what" of the platform.

This directory currently hosts the **rfantibody case** (the primary track below): it
reproduces the **RFantibody** pipeline (Bennett et al., de novo antibody design with
RFdiffusion) entirely through bioq — no local GPU, no environment setup — and
recovers the in-silico acceptance funnel.

## Claim

A discovery workflow that spans **mutually incompatible software stacks** runs as a
handful of laptop commands through bioq and yields **valid in-silico candidates** —
no local GPU, no environment management, minimal glue code.

## Rationale

The dependency-incompatibility audit (sibling analysis `dependency_incompatibility/`) proves the stacks are incompatible; this campaign shows the payoff of hiding that: a
biologist chains design → fold → score across those stacks as if they were one
tool. This is the concrete embodiment of "democratization".

## Protocol

### Primary track — de novo antibody / VHH (rfantibody, most mature subdomain)

The design → sequence → fold → filter chain:

1. **Design:** `bioq run rfantibody ...` (RFdiffusion) to produce N backbones
   against a target epitope.
2. **Sequence:** `bioq run proteinmpnn design ...` on the backbones.
3. **Fold:** `bioq run boltz predict ...` (or `esmfold2`) to predict complex
   structures.
4. **Filter/score:** `bioq run dockq score ...` and/or ipTM thresholds to select
   candidates.
5. Record the design **funnel** (N designed → M folded → K pass filters) and the
   exact commands.

**Realized (rfantibody case):** design + sequence + fold/score currently ship
inside one service (`rfantibody-server`) as three chained endpoints, so the
campaign is **three `bioq run` calls per target**:

```
rfdiffusion (target + framework) → 1_rfdiffusion.qv
proteinmpnn (1_rfdiffusion.qv)    → 2_proteinmpnn.qv
rf2         (2_proteinmpnn.qv)    → 3_rf2.qv   (structure prediction + pae_interaction scores)
```

Filtering is done offline from RF2's own `QV_SCORE` fields — interface pAE < 10 and
self-consistency RMSD < 2 Å (the paper's minimal filter) — rather than a separate
`dockq` call. This collapses the "across stacks" chain into one service's endpoints,
so the realized case is the single-service form; the fully cross-service form
(separate RFdiffusion / boltz / dockq services) remains the full-funnel target.

### Optional track — small molecule

`pocketxmol` (pocket-conditioned gen) → `diffdock` (dock) → `plip` (interaction
profile) → `openadmet` (ADMET) → `qligfep` (RBFE), same funnel reporting.

## Targets (9, reproducing the paper's Tables 5 & 7)

| Target | Type | PDB/file | Hotspot residues | Framework | diffuser_t |
|--------|------|----------|------------------|-----------|------------|
| HIV Env | VHH | 2NY7.pdb | G371,G375,G435,G475 | NbBCII10 | 100 |
| SARS-CoV-2 RBD | VHH | 6M0J.pdb | E492..E497 | NbBCII10 | 50 |
| RSV-F Site I | VHH | 7LVW.pdb | D469,D384 | NbBCII10 | 50 |
| RSV-F Site III | VHH | rsv_site3.pdb | T305,T456 | NbBCII10 | 50 |
| Influenza HA | VHH | flu_HA.pdb | B146,B170,B177 | NbBCII10 | 50 |
| TcdB | VHH | 6C0B.pdb | A1433..A1493 | NbBCII10 | 50 |
| IL-7Rα | VHH | 3DI3.pdb | B81,B139,B192 | NbBCII10 | 50 |
| TcdB scFv unique | scFv | 7ML7.pdb | A1816..A1831 | hu-4D5-8 | 50 |
| TcdB scFv combinatorial | scFv | 6C0B.pdb | A1433..A1493 | hu-4D5-8 | 50 |

## Usage

### 1. Stage inputs

```bash
bash fetch_inputs.sh
```

### 2. Activate the environment and set a writable state directory (optional)

`run_commands.sh` / `run_batched.sh` activate `.venv` on their own; if you run the
commands manually one by one, set up:

```bash
source ~/bioagent/.venv/bin/activate
export XDG_STATE_HOME=/tmp/bioq-state
mkdir -p /tmp/bioq-state
```

> The `proteinmpnn` / `rf2` steps re-upload the previous step's downloaded Quiver
> file via `--file input_quiver=<previous .qv>` (the server-side input port was
> renamed from `input_uri` to `input_quiver_uri` / `input_quiver`). Just run
> `bash run_commands.sh <target>`.

### 3. Run a single target

```bash
bash run_commands.sh RSV_Site_III      # VHH
bash run_commands.sh TcdB_scFv_unique  # scFv
```

### 4. Run all targets (serial)

```bash
bash run_commands.sh
```

### 5. Print all commands (for manual parallel execution)

```bash
bash run_commands.sh print
```

Then copy the `bioq run` commands of interest into multiple terminals to run in
parallel.

## Filter criteria (matching the paper)

Offline analysis uses the RFantibody paper's minimal "Filtering Strategies":

- **RF2 interface pAE < 10** → score field `interaction_pae` (the paper writes it
  as `pae_interaction`).
- **RMSD (design vs RF2 predicted) < 2 Å** → score field
  `framework_aligned_cdr_rmsd` (CDR self-consistency RMSD).

Each row in `3_rf2.qv` carries these real `QV_SCORE` fields
(`interaction_pae|pae|pred_lddt|target_aligned_*_rmsd|framework_aligned_*_rmsd`).
`config.py`'s `FILTER` maps to these real fields; `analyze.py` emits two tiers —
`pae_pass` (pAE filter only) and `passed_filter` (pAE + RMSD) — so the marginal
contribution of the RMSD filter can be read off.

## Metrics

- Candidates passing **published** in-silico filters (e.g. self-consistency RMSD
  < 2 Å, ipTM > threshold) — use upstream methods' own thresholds, do not invent.
- #distinct tools chained; **#incompatible environments avoided** (cross-reference the dependency-incompatibility audit).
- User-authored lines of code (should be ~one command per stage).
- Total wall-clock; local GPUs used (= 0).

## Controls / threats to validity

- Acceptance thresholds come from the upstream literature, cited — bioq is not
  claiming new success rates, only that the campaign is *runnable this easily*.
- Report the funnel honestly including drop-off; a low pass rate still supports the
  access claim (the point is feasibility of the workflow, not hit rate).
- Fix seeds / record digests so the campaign is reproducible.

## Files

The case files live directly in this directory (no per-case subdirectory yet).

- `config.py` — target definitions, parameters, and filters
- `fetch_inputs.sh` — download target PDBs + copy frameworks to `inputs/`
- `run_commands.sh` — **main entry**; explicit `bioq` commands for all targets
- `run_batch_dev.sh` — batch runner scripts
- `run_batched.sh` — batch helper (activates `.venv`, sets the writable state dir)
- `run_offline.sh` — offline analysis + plotting
- `analyze.py` — offline analysis; **streams** `batch_*/rf2/3_rf2.qv` (or
  `merged/3_rf2.qv`) → `data/<target>/{designs.csv,funnel.json,funnel.csv}` +
  `data/campaign_summary.csv`
- `merge_quivers.py` — merge `batch_*/<stage>/*.qv` into a single `merged/*.qv`
  (optional; `analyze` can read the batch files directly)
- `plot.py` — offline figures → `figures/rfantibody_campaign.pdf` /
  `figures/rfantibody_<target>.pdf`
- `plot_funnel.py` — per-target design-funnel grouped barplot (log-y):
  `python3 plot_funnel.py`
- `plot_pae.py` — 3×3 interaction-pAE histograms: `python3 plot_pae.py`
- `plot_rmsd.py` — 3×3 framework-aligned CDR RMSD histograms (<2 Å threshold):
  `python3 plot_rmsd.py`
- `plot_supplementary.py` — assemble all analysis panels into one supplementary
  figure (single PDF, width ≤16 cm): `python3 plot_supplementary.py`
- `make_mock.py` — fabricate mock data for offline testing
- `palette.py` — shared brand colors for figures
- `data/` — per-target `designs.csv` + funnel + `campaign_summary`
- `figures/` — generated figures
- `inputs/` — staged target + framework PDBs

## Notes

- The filesystem under `~/.config/bioq/tokens/` and `~/.local/state/bioq/jobs.json`
  is read-only; set `XDG_STATE_HOME=/tmp/bioq-state` for bioq to work.
- HIV_Env uses `diffuser_t=100` (other targets use 50) because its hotspot span is
  large and needs more diffusion steps to stay stable.

## Adding a case

Create a subdirectory mirroring this layout: point `config.py` at the new
service/endpoints, inputs, and the paper's reported in-silico numbers; keep the
collection-vs-offline split. The shared `palette.py` keeps figures consistent.

## Cases

| case | pipeline | paper | status |
|---|---|---|---|
| rfantibody | RFdiffusion → ProteinMPNN → RF2 (three endpoints of one service) | Bennett et al., de novo antibody design with RFdiffusion | implemented — 9 targets (7 VHH + 2 scFv), funnel + "vs paper" comparison generated; files in this directory |

## Outputs

- **Box / figure (end-to-end campaign):** command strip (one line per stage) beside the funnel counts.
- Cross-reference to the dependency-incompatibility audit for the "environments avoided" number.

## Data to record

Raw data lives in `data/` (per-target `designs.csv` + `funnel.{json,csv}`,
`campaign_summary.{csv,json}`) and figures under `figures/`. Also record the command
script(s), container digests, and the wall-clock log so every reported number is
regenerable from a committed script + raw log.