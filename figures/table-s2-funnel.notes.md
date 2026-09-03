# Supplementary Table S2 — E5 antibody-campaign funnel (notes)

Companion notes to `table-s2-funnel.csv`. That CSV is the per-target design
funnel for the nine-target RFantibody de novo antibody-design campaign (E5),
promoted from the private experiment outputs to the paper directory. It renders
as Table S2 in `latex/supplementary.tex`.

## Source (traceability)

Numbers come verbatim from
`end_to_end_campaign/data/campaign_summary.csv`
(machine-readable equivalent: `campaign_summary.json`), which
`analyze.py --from-data` regenerates from the per-design
`data/<target>/designs.csv`. The per-target `data/<target>/funnel.csv` files
carry the same stage counts. All nine targets agree on 1{,}000 / 8{,}000 / 8{,}000
backbones / sequences / scored; the per-design `designs.csv` row counts (8{,}001
lines = 8{,}000 designs + header) confirm the sequence counts.

The acceptance filter is the RFantibody paper's minimal in-silico criterion
(`config.py::FILTER`): `interaction_pae < 10` (interface pAE) **and**
`framework_aligned_cdr_rmsd < 2` Å (self-consistency CDR RMSD).

## Columns

| Column | Meaning |
|---|---|
| `target` | Canonical target key, identical to `campaign_summary.csv`. |
| `type` | `VHH` (nanobody, from `config.py VHH_TARGETS`) or `scFv` (from `SCFV_TARGETS`). |
| `backbones` | `rfdiffusion_backbones` — RFdiffusion-generated backbones. |
| `sequences` | `mpnn_sequences` — ProteinMPNN sequences (8 per backbone). |
| `scored` | `rf2_scored` — sequences carried through RoseTTAFold-2 folding + scoring. |
| `pae_pass` | Sequences passing `interaction_pae < 10` alone. |
| `passed` | `passed_filter` — sequences passing the combined filter (pAE < 10 AND CDR RMSD < 2 Å). |
| `passed_fraction` | `in_silico_pass_fraction` = `passed / scored` (per-sequence). |
| `backbone_pass` | Backbones whose best-of-8 MPNN sequence passes the combined filter. |
| `backbone_pass_fraction` | `backbone_pass / backbones` (best-of-8, per-backbone). |

## Two denominators (important)

- **`passed_fraction`** is the *per-sequence* pass rate (denominator = 8{,}000
  scored sequences). It is the funnel-yield fraction.
- **`backbone_pass_fraction`** is the *per-backbone* best-of-8 rate
  (denominator = 1{,}000 backbones), the metric the RFantibody paper reports and
  the one used for the main text's "2.4 % to 70.6 %" pass-rate range (RSV-F Site I
  $ightarrow$ SARS-CoV-2 RBD).

## Ordering

Rows are ordered by `backbone_pass_fraction` (descending), VHH block first
(seven rows) then scFv (two rows), matching how Table S2 is rendered.