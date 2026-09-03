#!/usr/bin/env bash
# Stage input files for the throughput-scaling analysis.
# Copies from service test data for all 6 services.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p inputs

# Root of the bioq-services repo (parallel to this path)
REPO="$(cd ../../.. && pwd)"

# Helper: copy a file from source to inputs/ if not already present
copy_if() {
  local src="$1" dest="inputs/$2"
  if [[ -s "$dest" ]]; then
    echo "have $dest"
  elif [[ -s "$src" ]]; then
    cp "$src" "$dest"
    echo "copied $src -> $dest"
  else
    echo "WARNING: $src not found"
  fi
}

# ---- proteinmpnn: 5L33.pdb (monomer) ----
copy_if "$REPO/bioq-services/services/proteinmpnn-server/tests/data/5L33.pdb" "5L33.pdb"

# ---- mmseqs2: sequence.fasta (short protein sequence for MSA search) ----
# Create a minimal FASTA with a short, well-known protein sequence
if [[ -s "inputs/sequence.fasta" ]]; then
  echo "have inputs/sequence.fasta"
else
  cat > inputs/sequence.fasta << 'EOF'
>sp|P68871|HBB_HUMAN Hemoglobin subunit beta
MVHLTPEEKSAVTALWGKVNVDEVGGEALGRLLVVYPWTQRFFESFGDLS
TPDAVMGNPKVKAHGKKVLGAFSDGLAHLDNLKGTFATLSELHCDKLHV
DPENFRLLGNVLVCVLAHHFGKEFTPPVQAAYQKVVAGVANALAHKYH
EOF
  echo "created inputs/sequence.fasta (HBB_HUMAN, 147 aa)"
fi

# ---- rfdiffusion2: no input files ----
echo "rfdiffusion2 custom endpoint: no input files needed"

# ---- reinvent: no input files (standalone sampling) ----
echo "reinvent sampling endpoint: no input files needed"

# ---- rfdiffusion (v1): no input files (unconditional) ----
echo "rfdiffusion unconditional endpoint: no input files needed"

# ---- boltz: no input files (inline sequences via --set-json) ----
echo "boltz predict_structure endpoint: no input files needed"

# ---- boltzgen: vanilla.yaml (design YAML) ----
copy_if "$REPO/bioq-services/services/boltzgen-server/tests/data/vanilla.yaml" "vanilla.yaml"

# ---- alphafold: bench.fasta (short protein sequence) ----
if [[ -s "inputs/bench.fasta" ]]; then
  echo "have inputs/bench.fasta"
else
  cat > inputs/bench.fasta << 'EOF'
>bench_protein
MKTAYIAKQRQISFVKSHFSRQLE
EOF
  echo "created inputs/bench.fasta (25 aa)"
fi

# ---- plip: 1vsn.pdb (protein-ligand complex) ----
copy_if "$REPO/bioq-services/services/plip-server/tests/data/1vsn.pdb" "1vsn.pdb"

# ---- dockq: model.pdb + native.pdb ----
copy_if "$REPO/bioq-services/services/dockq-server/tests/data/model.pdb" "model.pdb"
copy_if "$REPO/bioq-services/services/dockq-server/tests/data/native.pdb" "native.pdb"

echo "done. inputs in ./inputs/"
ls -la inputs/