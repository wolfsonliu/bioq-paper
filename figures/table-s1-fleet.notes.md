# Supplementary Table S1 — full fleet (notes)

Companion notes to `table-s1-fleet.csv`. That CSV is the 38-row fleet table
mapped from `services.yaml` + `bioq describe` (`manifests/*.manifest.json`)

## Columns

| Column | Meaning |
|---|---|
| `short_name` | Registry key without the `-server` suffix (as printed by `bioq services`). |
| `stage` | The 7 discovery stages, numbered 1–7. |
| `modality` | Modality codes from `coverage-matrix.md`. Legend: `P`=protein, `Ab`=antibody/VHH, `SM`=small molecule, `Pep`=peptide, `NA`=nucleic acid, `X`=cross-modal. |
| `upstream_method` | The upstream tool/method the service wraps (from the manifest `service_specific.model` / the service README). |
| `citation` | Semicolon-separated Better-BibTeX citation keys, resolved in `paper/references.bib`. |
| `citation_status` | `in_bib` = all keys present in `paper/references.bib`; `none` = no citable upstream publication. |

## Citation status

37 of 38 rows are `in_bib` (all keys resolve in `paper/references.bib`). The one
`none` row is `ensemble` — a platform-native multi-method aggregation layer
(orchestrating AlphaFold / ESMFold / Boltz / Promera) with no upstream paper of
its own; the component methods are each cited on their own rows.

## Newly imported references (added to `paper/references.bib`)

These 12 fleet-method references were exported from Zotero (Better-BibTeX format)
and appended to `paper/references.bib`; keys are the real BBT keys:

| Key | Method (service) |
|---|---|
| `buchfink_clustering_2026` | DIAMOND DeepClust (diamond) — Nat Methods 2026, 10.1038/s41592-026-03030-z |
| `ahern_atom-level_2026` | RFdiffusion2 (rfdiffusion2) — Nat Methods 2026, 10.1038/s41592-025-02975-x |
| `krishna_generalized_2024` | RoseTTAFold All-Atom / RFdiffusion-All-Atom (rfdiffusion2 base) — Science 2024, 10.1126/science.adl2528 |
| `yu_high-affinity_2026` | PPIFlow (ppiflow) — bioRxiv 2026 |
| `stark_boltzgen_2025` | BoltzGen (boltzgen) — bioRxiv 2025, 10.1101/2025.11.20.689494 |
| `wang_iggm_2025` | IgGM (iggm) — ICLR 2025 |
| `zhang_odesign_2025` | ODesign (odesign) — arXiv:2510.22304 |
| `fry_zero-shot_2026` | NISE / LASErMPNN (lasermpnn) — Nature 2026, 10.1038/s41586-026-10670-w |
| `weller_structure-based_2024` | DrugHIVE (drughive) — J Chem Inf Model 2024, 10.1021/acs.jcim.4c01193 |
| `jang_chembounce_2025` | ChemBounce (chembounce) — Bioinformatics 2025, 10.1093/bioinformatics/btaf501 |
| `torge_diffhopp_2023` | DiffHopp (diffusion-hopping) — arXiv:2308.07416 |
| `yoo_turbohopp_2024` | TurboHopp (turbohopp) — NeurIPS 2024, arXiv:2410.20660 |

Notes on attribution:

- **RFdiffusion2** row cites **both** `ahern_atom-level_2026` (the actual
  RFdiffusion2 paper, what `rfdiffusion2-server` wraps) and
  `krishna_generalized_2024` (RFAA / RFdiffusion-All-Atom, its all-atom base) —
  per author decision. The DOI `10.1126/science.adl2528` supplied for
  "RFdiffusion2" resolves to the RFAA paper, not RFdiffusion2; both are now cited.
- **DIAMOND** row cites the DeepClust paper (`buchfink_clustering_2026`) per the
  supplied DOI, rather than the 2015 DIAMOND aligner paper.
- **ChemBounce** previously had no citable paper; a Bioinformatics 2025
  application note now exists and is cited.