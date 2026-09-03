# DeepRank-Ab Inference Pipeline

DeepRank-Ab is a scoring function for ranking
antibody-antigen docking models based on geometric deep learning.


📄 **Publication**\
https://www.biorxiv.org/content/10.64898/2025.12.03.691974v1

This repository provides the **full inference pipeline** for the model
described in the paper.

------------------------------------------------------------------------

## 🚀 Features

-   **PDB Processing**
    -   Split ensemble models 
    -   Extract chain sequences 
    -   Merge chains for downstream analysis 
-   **FASTA Conversion**
    -   Generate FASTA files for CDR annotation and ESM embeddings 
-   **ESM Embeddings**
    -   Compute embeddings using `esm2_t33_650M_UR50D` 
-   **Graph Construction**
    -   Build atom-level graphs with precomputed node and edge features 
-   **Prediction**
    -   Inference with pretrained EGNN models and output predicted DockQ

------------------------------------------------------------------------

## 📦 Installation

### 1. Clone the repository

``` bash
git clone https://github.com/haddocking/DeepRank-Ab
cd DeepRank-Ab
```

### 2. Create and activate the environment

``` bash
mamba env create -f environment-gpu.yml
mamba activate deeprank-ab
```

### 3. Install ANARCI

ANARCI is required for CDR annotation.

Installation instructions:\
https://github.com/oxpig/ANARCI

*Note:* `hmmscan` is already included in the environment.\
If you encounter issues, follow the workaround here:\
https://github.com/oxpig/ANARCI/issues/102

------------------------------------------------------------------------

## 🔧 Usage

The inference pipeline is executed through:

    DeepRank-Ab/scripts/inference.py

### **Run the pipeline**

``` bash
python3 scripts/inference.py <pdb_file> <antibody_heavy_chain_id> <antibody_light_chain_id> <antigen_chain_id>
```

### **Example**

``` bash
python3 scripts/inference.py example/test.pdb H L A
```

This will:

-   Create a workspace
-   Generate ESM embeddings
-   Annotate CDRs
-   Build atom-level graphs
-   Cluster nodes
-   Predict DockQ scores
-   Save output files (`.csv` and `.hdf5`)

------------------------------------------------------------------------

## 🧬 Input Requirements

-   **PDB file**\
    Antibody--antigen structure. Can be a single model or an ensemble.

-   **Heavy chain ID**\
    Example: `H`

-   **Light chain ID**\
    Example: `L`

-   **Antigen chain ID**\
    Example: `A`

------------------------------------------------------------------------


## ⚙️ Large-Scale Inference

We provide a helper script for running DeepRank-Ab on **large batches**
of complexes. Adapt it to your dataset as needed. 

Example:

``` bash
python3 scripts/run_batch_inference.sh
```

------------------------------------------------------------------------

## 📫 Support

For issues or questions, please open a GitHub issue.
