# Footprint audit (storage) — image size vs the bioq thin client

**Role:** support for the access-barrier claim — the storage-footprint half of
Figure S3 (panel b). **Feasibility:** computable now (best-effort `docker image ls`
+ a throwaway client venv). No cloud required.

Records the on-disk size of each locally-built bioq-services image and measures the
bioq client install footprint, then contrasts the fleet aggregate against the
client. Moved out of `dependency_incompatibility/` (where it was "Part C") so each
analysis folder stands alone; the dependency-incompatibility analysis still reads
`data/signatures.csv` (the stack-signature table) from this folder as its
coarse-incompatibility evidence.

## Claim

Accessing the full fleet natively means hauling ≈ 298 GB-and-counting of Docker
images; bioq replaces this with a thin client whose only direct runtime dependency
is `httpx` (measured install ≈ 99.6 MB). Footprint is a partial lower bound, not a
precise total (see **Threats**).

## Method

`collect_footprint.py` is best-effort: it enumerates services from
`data/signatures.csv` (the committed stack-signature table), sizes whatever images
are built locally via `docker image ls`, and measures the bioq client by installing
`httpx` into a throwaway venv and summing file sizes. `plot.py` renders the figure
offline from `data/footprint.csv` (it never touches Docker or a venv).

## Results (regenerated from the current repo)

| Metric | Value |
|---|---|
| Service images measured | **33 / 38** (5 not built on this host) |
| Measured fleet total (partial sum) | **≈ 298 GB** |
| Smallest service image | ensemble 232 MB |
| Largest service image | rfdiffusion2 21.1 GB |
| bioq client install (measured fresh venv + `httpx`) | **99.6 MB** |
| bioq client direct runtime dependency | **1** (`httpx`) |

The unmeasured images (diamond, haddock3, lasermpnn, odesign, turbohopp) only push
the fleet total higher. The measured client install (99.6 MB, including the Python
runtime and `httpx`'s transitive deps) is already ≈ 90× smaller than an *average*
service image (~9 GB) and ≈ 3000× smaller than the measured fleet aggregate; the
client *package* itself is ~1.8 MB.

## How to run

`uv` is needed for the footprint steps; `docker` is needed for image sizing.
`data/signatures.csv` is committed input.

```bash
uv run --with matplotlib python collect_footprint.py   # data/signatures.csv -> data/footprint.csv
uv run --with matplotlib python plot.py                # -> figures/… (footprint bar chart)
```

`collect_footprint.py` is best-effort: it sizes whatever images are built locally
and measures the bioq client venv; images not on this host are left unmeasured.

## Files

- `data/signatures.csv` — per-service stack signature (base kind, CUDA major.minor +
  devel/runtime, Ubuntu, Python, torch pin) with provenance column; committed input
  (also read by `../dependency_incompatibility/` for its coarse-incompatibility
  evidence).
- `data/footprint.csv` — per-service image size + bioq client (collection output).
- `collect_footprint.py` — best-effort image sizes (`docker image ls`) + bioq client
  venv measurement; writes `data/footprint.csv`.
- `plot.py` — offline render of the footprint figure from `data/footprint.csv`.
- `figures/footprint.pdf` — log-scale footprint bar chart (committed render).

## Threats to validity & honest caveats (state in the paper)

- **Footprint is partial.** 33/38 images measured locally; the fleet total is a
  lower bound (~298 GB and counting). The client-vs-image contrast holds even
  against the *smallest* service image (ensemble, 232 MB).
- **Footprint "avoided" assumes the user actually needs multiple tools**; state this
  in the paper.
