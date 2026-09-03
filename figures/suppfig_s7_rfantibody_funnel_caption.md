**Figure S7.** Per-target design funnel for the nine-target RFantibody de novo
antibody-design campaign run entirely through bioq (three `bioq run` calls per
target, no local GPU). For each target, five grouped vertical bars report the
count at successive pipeline stages: RFdiffusion backbones (1,000), ProteinMPNN
sequences (8,000 = 8 sequences per backbone), sequences carried through RF2
structure prediction and scoring (8,000), designs passing the interface-pAE < 10
filter, and designs passing the combined acceptance criterion (interface pAE < 10
and framework-aligned CDR RMSD < 2 Å; amber). The y-axis is log-scaled
because the funnel spans two orders of magnitude, from 37 to 8,000 designs.