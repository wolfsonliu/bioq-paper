# tinyprot

`tinyprot` is a lightweight library for loading and manipulating biomolecular structures. It is designed for use cases in biomolecular machine learning and seeks to strip away as many unecessary abstractions as possible. `tinyprot` is meant to be simple enough to understand in one sitting (this README serves as comprehensive documentation) but powerful enough for any standard task in biomolecular machine learning.

**Contents:** [Installation](#installation) · [Chain](#chain) · [Structure](#structure) · [MSAs](#msas) · [Cropping](#cropping) · [Tokenization](#tokenization) · [Featurization](#featurization) · [Scoring](#scoring-structures)

---

## Capabilities

* Load and process CIFs
* Crop and featurize structures
* Handle, cache, and pair MSAs
* Compare structures via LDDT and DockQ

## Dependencies

We seek to make `tinyprot` as simple as possible; it is built from scratch on top of `numpy`, `pandas`, and pure python. Biomolecular structures are handled directly, without the legacy interfaces of `biotite`, `biopython`, `rdkit`, `gemmi`, etc.

## Installation

1. Install the package and dependencies

```bash
pip install git+https://github.com/bjing2016/tinyprot.git
```

2. Set the cache directory. By default, the package will use `$HOME/.cache/tinyprot`. If an alternate path is desired, set `TINYPROT_CACHE`.

3. Download CCD and taxonomy databases.

```bash
# build from scratch
python -m tinyprot.init --build

# or download from HuggingFace
python -m tinyprot.init --download
```

---

## Loading and manipulating structures

### `Chain`

The fundamental abstraction in `tinyprot` is a `Chain` object, which represents the atomic structure of a single molecule (unique `label_asym_id`). It has the attributes

| Attribute | Shape | Description |
|-----------|-------|-------------|
| `coords` | (N × M × 3) float | Atomic positions |
| `mask` | (N × M) bool | `True` if atom is present |
| `aname` | (N × M) str | Atom names, e.g. `CA` |
| `asymb` | (N × M) str | Element symbols, e.g. `C` |
| `rname` | (N,) str | Residue names, e.g. `GLY` |
| `ridx` | (N,) int | Residue indices (`label_seq_id` for polymers) |
| `asym_id` | str | Chain label, e.g. `A` |
| `entity_id` | str | Entity label, e.g. `1` |
| `type` | str | One of `non-polymer`, `branched:oligosaccharide`, `polymer:polypeptide(L)`, `polymer:polyribonucleotide`, `polymer:polydeoxyribonucleotide` |
| `seq` | str (optional) | Single-letter sequence string for MSA lookup |

where N is the number of residues and M is the maximum number of atoms per residue (grid format, padded to the largest residue via the CCD). `Chain`s are instantiated when constructing `Structure` objects, described below.

### `Structure`

A `Structure` is a thin wrapper around a set of chains with the attributes:

| Attribute | Description |
|-----------|-------------|
| `chains` | `dict` from `asym_id` → `Chain` |
| `connections` | Pandas DataFrame of covalent bonds from `_struct_conn`, or `None`. Columns: `chain1`, `ridx1`, `aname1`, `chain2`, `ridx2`, `aname2` |
| `assemblies` | Dict of biological assembly transforms from the mmCIF, or `None` |

**Reading/writing mmCIF**

* `Structure.from_mmcif(path)` — load a `.cif` or `.cif.gz` file. Atom arrays are populated in canonical CCD order, with missing atoms marked `mask=False`. Residue indices follow `label_seq_id` for polymers, `auth_seq_id` for branched chains, and `1` for non-polymers. To load from a multi-model CIF file, pass `model_num=i`.
* `Structure.from_single_chain_mmcif(path)` — load a single-chain `.cif` or `.cif.gz` that lacks full mmCIF metadata (e.g. AlphaFold predictions). The chain is assigned `asym_id="A"` and `entity_id=1`.
* `.to_mmcif(path=None, metadata=False, models=None)` — write to `.cif` or `.cif.gz`, or return a CIF string if `path=None`. Set `metadata=True` to write CIF files representing full structures; set `metadata=False` for atom arrays or motifs that do not have standard ordinals for `ridx`. Pass `models` as a list of `{asym_id: coords}` dicts to write multiple MODEL blocks (e.g. for animations).

> [!WARNING]
> At present, all `label_seq_id`s must be present in the CCD (no `LIG`-style ligand codes).

**Schemas**

Structures can be constructed from or serialized to a simple JSON-compatible dict:

```python
schema = {
    "A": {
        "type": "protein",
        "sequence": "ACXEFG...",        # use X (unknown) at modified positions
        "modifications": {"3": "SEP"},  # 1-indexed; position must be X/N in sequence
        "entity_id": 1,                 # optional; defaults to chain order (1, 2, ...)
    },
    "B": {"type": "rna", "sequence": "AUGC..."},
    "C": {"type": "ligand", "sequence": "ATP"},
    "D": {"type": "branched", "sequence": ["NAG", "FUC"]},
    "connections": [
        {"chain1": "A", "ridx1": 42, "aname1": "SG",
         "chain2": "C", "ridx2": 1,  "aname2": "PA"}
    ]
}
struct = Structure.from_schema(schema)
schema = struct.to_schema()
```

Polymer sequences use single-letter codes; non-standard residues are written as the "unknown" single-letter code for their polymer type (`X` for protein, `N` for RNA/DNA) and spelled out as CCD codes in `modifications`. `entity_id` is optional and defaults to the chain's position in the dict (1-indexed). Chains sharing an `entity_id` are treated as copies of the same molecule.

> [!WARNING]
> At present, small molecules must be present in the CCD.

**Assemblies**

* `.get_assembly(i)` — apply biological assembly `i` (as labeled in the mmCIF), returning a new `Structure` with chains renamed `A1`, `A2`, etc.

**Other methods**

* `.locate(chain, ridx, aname, attr='coords')` — return the value of `attr` for a specific atom, or `None` if not found.
* `.transform(R=None, t=None)` — apply rotation `R` (3 × 3) and/or translation `t` (3,) to all chain coordinates in-place.
* `.restrict_to(other, mapping=None)` — overwrite this structure's `mask` arrays with those from `other` (useful for restricting a prediction to resolved atoms from a reference).
* `.count_chain_symmetries(include_ligands=False)` — return the number of valid chain permutations (product of factorials of same-entity chain-group sizes). Pass `include_ligands=True` to also count ligand chains.
* `.get_chain_symmetries(include_ligands=False, max_symmetries=None)` — return a list of `{ref_chain_id: pred_chain_id}` dicts enumerating all valid chain permutations. Pass `max_symmetries` to cap the list length.

---

## MSAs

`tinyprot` stores MSAs on disk as `.a3m.gz` files, keyed by the SHA-256 hash of the query sequence. This makes lookups O(1) and lets multiple experiments share a single MSA cache. If an MSA is not found for a given sequence, a dummy single-sequence MSA is returned silently so pipelines don't need to special-case missing data.

**Generating MSAs**

Use `python -m tinyprot.mmseqs2` to populate the MSA cache. It accepts a FASTA file, a directory of FASTA files, or a directory of schema JSON files as input and writes hashed `.a3m.gz` files to `--msa_dir` (defaults to `$TINYPROT_CACHE/msa`). Sequences already present in the cache are skipped unless `--overwrite` is set.

```bash
# Remote ColabFold API
python -m tinyprot.mmseqs2 --input seqs.fasta --url https://api.colabfold.com

# Local MMseqs2 database
python -m tinyprot.mmseqs2 --input seqs.fasta --db /path/to/colabfold_db
```

**`MSA` object**

| Attribute | Shape | Description |
|-----------|-------|-------------|
| `seqs` | (N × L) char | Residue letters including gaps `-` |
| `dels` | (N × L) int | Insertions (lowercase letters) before each position |
| `taxs` | (N,) int | NCBI taxonomy ID, or `-1` if unavailable |
| `path` | str | File the MSA was loaded from |

**Loading**

* `MSA.from_a3m(path)` — read a `.a3m` or `.a3m.gz` file. Taxonomy IDs are looked up from the taxonomy LMDB using `UniRef100_*` headers.
* `MSA.subsample(max_seqs)` — randomly subsample to `max_seqs` rows, always keeping the query (row 0).
* `load_msa_from_dir(path, seq)` — load an MSA from a directory of `.a3m[.gz]` files named by the SHA-256 hash of the query sequence. `seq` can be a string, a `Chain`, or a dict/list thereof. Returns a dummy single-sequence MSA if not found. `path` defaults to `$TINYPROT_CACHE/msa` if `None`.
* `msa_exists_in_dir(path, seq)` — return the path to the cached `.a3m[.gz]` file if it exists, or `False` if not. Useful for checking cache status before launching a search job.

**Pairing**

* `construct_paired_msa(msas, max_pairs=8192, max_total=16384, strategy='protenix')` — build a paired MSA table for a multi-chain complex. `msas` is a `{chain_id: MSA}` dict. `strategy` is one of `"boltz"`, `"protenix"`, or `"openfold"`. Returns `(pairing, is_paired)`: two parallel lists of dicts mapping `chain_id` to sequence index (`-1` = gap) and `0`/`1` paired indicator respectively.

---

## Cropping and featurization

### Cropping

`AF3Cropper` implements the AF3 / Boltz-1 spatial cropping algorithm. Starting from a center atom, it greedily expands a residue neighborhood until the token or atom budget is exhausted.

```python
from tinyprot.crop import AF3Cropper

cropped = AF3Cropper(struct).crop(
    center=('A', 42, 'CA'),  # (chain_id, ridx, aname) or an (x, y, z) coordinate
    max_tokens=384,
    max_atoms=3456,
    neighborhood=20,
)
```

The result is a new `Structure` containing only the cropped chains and residues, with `connections` filtered to atoms present in the crop.

### Tokenization

`AF3Tokenizer` assigns tokens to atoms according to the AF3 scheme and must be run before cropping or featurization (both call it internally). Standard residues get one token per residue; non-standard residues (ligands, modified residues) get one token per atom.

```python
from tinyprot.tokenize import AF3Tokenizer

AF3Tokenizer(struct).tokenize()
```

This adds the following attributes to each `Chain` in-place:

| Attribute | Shape | Description |
|-----------|-------|-------------|
| `tidx` | (N × M) int | Token index for each atom slot (`-1` for padding) |
| `aidx` | (N × M) int | Flat atom index across the whole structure |
| `is_token` | (N × M) bool | `True` for the representative atom of each token |

And sets `struct.tokens` — a list of `(chain_id, residue_idx, atom_idx)` tuples, one per token.

**Representative atoms** for standard residues:

| Molecule | Residues | Representative atom |
|----------|----------|---------------------|
| Protein | all except GLY/UNK | `CB` |
| Protein | GLY, UNK | `CA` |
| RNA/DNA purines | A, G, DA, DG | `C4` |
| RNA/DNA pyrimidines | C, U, DC, DT | `C2` |
| Unknown nucleotides | N, DN | `C1'` |

### Featurization

`AF3Featurizer` converts a `Structure` and optional paired MSAs into a dict of `numpy` arrays matching the AF3 input format.

```python
from tinyprot.feature import AF3Featurizer

feats = AF3Featurizer(struct, msas=msas, pairing=pairing).featurize()
```

`pairing` should be the `(pairing, is_paired)` tuple returned by `construct_paired_msa`. The returned dict contains the following arrays (A = number of atoms, T = number of tokens, N = number of MSA rows, B = number of bonds, V = vocabulary size):

<details>
<summary><strong>Atom-level features</strong></summary>

| Key | Shape | Description |
|-----|-------|-------------|
| `atom_coords` | (A × 3) | Observed coordinates |
| `atom_resolved_mask` | (A,) bool | `True` if atom is present |
| `atom_to_token` | (A,) int | Token index for this atom |
| `ref_pos` | (A × 3) | CCD ideal conformer coordinates |
| `ref_element` | (A,) int | Atomic number |
| `ref_charge` | (A,) int | Formal charge |
| `ref_hydrogens` | (A,) int | Number of attached hydrogens |
| `ref_atom_name` | (A,) str | Atom name, e.g. `CA` |
| `ref_atom_name_chars` | (A × 4) int | Atom name as ASCII offsets |
| `ref_space_uid` | (A,) int | Residue index for this atom |

</details>

<details>
<summary><strong>Token-level features</strong></summary>

| Key | Shape | Description |
|-----|-------|-------------|
| `restype` | (T,) int | Token type index (34-token vocabulary) |
| `residue_index` | (T,) int | Residue index in the chain |
| `residue_name` | (T,) str | CCD residue name, e.g. `GLY` |
| `asym_id` | (T,) int | Numeric chain index (0-based) |
| `asym_id_` | (T,) str | Chain label, e.g. `A` |
| `entity_id` | (T,) int | Numeric entity index (0-based) |
| `entity_id_` | (T,) str | Entity label |
| `sym_id` | (T,) int | Copy index within entity (0-based) |
| `is_protein`, `is_rna`, `is_dna`, `is_ligand` | (T,) int | Chain-type indicators |
| `is_std` | (T,) bool | Whether residue is a standard CCD type |
| `token_index` | (T,) int | Global token index |
| `token_pos` | (T × 3) float | Position of the representative atom |
| `token_pos_mask` | (T,) bool | Whether the representative atom is resolved |
| `token_to_rep_atom` | (T,) int | Flat atom index of the representative atom |
| `token_bonds` | (B × 2) int | Token pairs connected by covalent bonds |

</details>

<details>
<summary><strong>MSA features</strong> (only present if <code>msas</code> is provided)</summary>

| Key | Shape | Description |
|-----|-------|-------------|
| `msa_chars` | (N × T) char | MSA sequences including gaps |
| `msa` | (N × T) int | MSA sequences as token indices |
| `msa_mask` | (N × T) bool | |
| `msa_paired` | (N × T) bool | Whether this row is paired for this token's chain |
| `deletion_value` | (N × T) float | Arctan-scaled insertion count |
| `has_deletion` | (N × T) bool | |
| `deletion_mean` | (T,) float | Mean insertion count per position |
| `profile` | (T × V) float | Empirical residue frequency profile |

</details>

<details>
<summary><strong>Frame features</strong> (pass <code>compute_frames=True</code>)</summary>

| Key | Shape | Description |
|-----|-------|-------------|
| `frames_idx` | (T × 3) int | Atom indices of the three frame-defining atoms |
| `frames_mask` | (T,) bool | `True` for standard residues with a defined frame |

</details>

---

## Scoring structures

All scoring functions handle chain-level symmetry automatically, searching over all valid chain permutations. Note that we use a 15 A for all molecule types, including RNA/DNA.

### Per-chain LDDT

```python
from tinyprot.metrics import LDDT

result = LDDT(ref_chain, pred_chain)
# {'LDDT': float, 'count': int}

result = LDDT(ref_chain, pred_chain, per_atom=True)
# {'LDDT': (A,) array, 'valid_mask': (A,) bool}
```

### Interface LDDT

```python
from tinyprot.metrics import iLDDT

result = iLDDT(refA, refB, predA, predB)
# {'LDDT': float, 'count': int}
```

Computes LDDT over cross-chain atom pairs within 15 Å, without the intra-chain pairs included in `LDDT`. Useful for evaluating interface quality between a specific pair of chains.

### Complex LDDT

```python
from tinyprot.metrics import complex_LDDT

score, breakdown = complex_LDDT(ref_struct, pred_struct)
# score: float — aggregate over all chain pairs
# breakdown: {(chainA, chainB): {'LDDT': float, 'count': int}, ...}
```

`complex_LDDT` searches over both chain-level symmetries and, for non-polymer ligands, CCD atom symmetries. Pass a `mapping` dict (`{ref_chain_id: pred_chain_id}`) to skip the chain symmetry search. Set `permute_ligands=False` to skip atom symmetry search; `max_ligand_symmetries` caps it when enabled.

### DockQ

```python
from tinyprot.metrics import dockQ

result = dockQ(ref_struct, pred_struct)
# {(chainA, chainB): {'fnat': float, 'iRMSD': float, 'LRMSD': float, 'DockQ': float}, ...}
```

DockQ is computed for every pair of polymer chains with a non-zero interface. Set `exclude_nonstd=False` to include non-standard residues. Pass `mapping` to fix the chain assignment.

---

## License

MIT. Other licenses may apply to third-party source code noted in comments / file headers.

## Acknowledgements

Parts of this package were started from https://github.com/jwohlwend/boltz, https://github.com/sokrypton/colabfold, and https://github.com/biopython/biopython. A big thanks to the developers of these open-source libraries.
