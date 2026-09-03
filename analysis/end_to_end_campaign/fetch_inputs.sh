#!/usr/bin/env bash
# Stage the RFantibody inputs — target PDBs + frameworks — into ./inputs/.
#
# For every target we download from RCSB we do a mandatory cleanup pass:
#   - keep the epitope chain only (drops other chains, e.g. co-crystallized
#     Fab H+L in 2NY7)
#   - drop HETATM (waters, glycans, ligands)
#   - keep first NMR MODEL only
#   - resolve alt-locs (keep blank + 'A')
#   - keep the 20 standard amino acids (MSE normalised to MET)
#   - crop to a 12 Å shell around the hotspot CAs (any heavy atom within radius,
#     plus the hotspot residues themselves)
# Raw downloads are preserved under inputs/raw/ for reproducibility; the file
# consumed by bioq is the cleaned inputs/<pdbid>.pdb (matches config.py paths).
#
# Rationale: RFdiffusion Ab fails on raw 2NY7 with "Non-positive determinant in
# rotation matrix …" — a degenerate backbone frame produced by feeding the full
# ~1000-residue asymmetric unit (chains G+H+L + glycans, jagged G numbering).
# Cropping to the epitope shell around G371/G375/G435/G475 removes the noise,
# matches the RFantibody paper's protocol, and gives a numerically stable target.
#
# Fully reproducible; idempotent (re-run only rebuilds files older than their raw
# source or missing).

set -euo pipefail
cd "$(dirname "$0")"
mkdir -p inputs inputs/raw

RFAB_SRC="${RFAB_SRC:-../../compute_barrier/opensource/RFantibody/scripts/examples/example_inputs}"
CROP_RADIUS="${RFAB_CROP_RADIUS:-12}"   # Å — override via env if needed

# -------------------------------------------------------------------------
# Helper: download a raw PDB (once)
# -------------------------------------------------------------------------
dl_pdb() {
  local pdb_id="$1" label="$2"
  local raw="inputs/raw/${pdb_id}.pdb"
  if [[ -s "$raw" ]]; then
    echo "have raw/${pdb_id}.pdb  ($label)"
    return 0
  fi
  echo "downloading ${pdb_id} ($label) ..."
  curl -fsSL "https://files.rcsb.org/download/${pdb_id}.pdb" -o "$raw"
  local sz
  sz=$(stat -c%s "$raw" 2>/dev/null || stat -f%z "$raw")
  echo "  ok (${sz} bytes)"
}

# -------------------------------------------------------------------------
# Helper: clean + crop a downloaded target for RFantibody consumption
#   clean_target <pdb_id> <chain> <hotspots-csv>
# Writes inputs/<pdb_id>.pdb. Fails loudly if any hotspot residue is missing
# from the chosen chain after filtering.
# -------------------------------------------------------------------------
clean_target() {
  local pdb_id="$1" chain="$2" hotspots="$3"
  local raw="inputs/raw/${pdb_id}.pdb"
  local out="inputs/${pdb_id}.pdb"
  if [[ -s "$out" && "$out" -nt "$raw" ]]; then
    echo "have cleaned inputs/${pdb_id}.pdb"
    return 0
  fi
  RFAB_RAW="$raw" RFAB_OUT="$out" RFAB_CHAIN="$chain" \
  RFAB_HOTSPOTS="$hotspots" RFAB_RADIUS="$CROP_RADIUS" \
  python3 - <<'PY'
import os, re, sys

raw     = os.environ["RFAB_RAW"]
out     = os.environ["RFAB_OUT"]
chain   = os.environ["RFAB_CHAIN"]
hs_arg  = os.environ["RFAB_HOTSPOTS"]
radius  = float(os.environ["RFAB_RADIUS"])

STD = {"ALA","ARG","ASN","ASP","CYS","GLN","GLU","GLY","HIS","ILE","LEU","LYS",
       "MET","PHE","PRO","SER","THR","TRP","TYR","VAL"}

# Hotspots like "G371,G375" -> {(chain, int_resi)}
hotspots = []
for h in hs_arg.split(","):
    h = h.strip()
    if not h:
        continue
    m = re.match(r"^([A-Za-z])(-?\d+)$", h)
    if not m:
        sys.exit(f"error: malformed hotspot '{h}' (expected e.g. G371)")
    hotspots.append((m.group(1), int(m.group(2))))
hs_set = set(hotspots)

# Read: chain match, first MODEL only, ATOM (or MSE HETATM), alt-loc blank/A.
# Normalise MSE->MET (selenomethionine, common in crystal structures).
kept: list[str] = []
in_model = True   # allow all lines before any MODEL/ENDMDL
seen_model_end = False
for line in open(raw, encoding="utf-8", errors="replace"):
    if line.startswith("MODEL "):
        in_model = (not seen_model_end)
        continue
    if line.startswith("ENDMDL"):
        seen_model_end = True
        in_model = False
        continue
    if not in_model:
        continue
    if not (line.startswith("ATOM  ") or line.startswith("HETATM")):
        continue
    rec = line[:6]
    alt = line[16]
    resn = line[17:20].strip()
    ch = line[21]
    try:
        resi = int(line[22:26])
    except ValueError:
        continue
    if ch != chain:
        continue
    if alt not in (" ", "A"):
        continue
    # Selenomethionine -> methionine
    if resn == "MSE":
        line = "ATOM  " + line[6:17] + "MET" + line[20:]
        atom = line[12:16]
        if atom.strip() == "SE":
            line = line[:12] + " SD " + line[16:]
    elif resn not in STD:
        continue
    else:
        # force to ATOM record for the standard 20
        line = "ATOM  " + line[6:]
    # Blank alt-loc column so downstream tools don't re-see 'A'
    line = line[:16] + " " + line[17:]
    kept.append(line)

if not kept:
    sys.exit(f"error: no ATOM records survived for chain {chain} in {raw}")

def xyz(ln):
    return (float(ln[30:38]), float(ln[38:46]), float(ln[46:54]))

# Locate hotspot CA coordinates
hs_xyz = []
missing = set(hs_set)
for ln in kept:
    if ln[12:16].strip() != "CA":
        continue
    key = (ln[21], int(ln[22:26]))
    if key in hs_set:
        hs_xyz.append(xyz(ln))
        missing.discard(key)
if hs_set and missing:
    sys.exit(f"error: hotspot residues missing from chain {chain} of {raw}: "
             + ", ".join(f"{c}{r}" for c, r in sorted(missing)))

# Crop: keep any residue with a heavy atom within `radius` Å of any hotspot CA,
# plus the hotspot residues themselves. If no hotspots, keep everything.
if hs_xyz:
    r2 = radius * radius
    selected = set(hs_set)
    for ln in kept:
        if ln[76:78].strip() == "H":
            continue
        x, y, z = xyz(ln)
        for hx, hy, hz in hs_xyz:
            if (x - hx) ** 2 + (y - hy) ** 2 + (z - hz) ** 2 <= r2:
                selected.add((ln[21], int(ln[22:26])))
                break
    kept = [ln for ln in kept if (ln[21], int(ln[22:26])) in selected]
    n_shell = len(selected) - len(hs_set)
    tag = f" (12 Å shell around {len(hs_set)} hotspots: {n_shell} + {len(hs_set)} = "
    tag += f"{len(selected)} residues)"
else:
    tag = ""

# Re-serial atom numbers; write with a small provenance REMARK.
serial = 1
with open(out, "w", encoding="utf-8") as f:
    f.write(f"REMARK bioq preprocess: chain={chain} radius={radius:.1f} "
            f"hotspots={hs_arg or 'none'}\n")
    for ln in kept:
        f.write(ln[:6] + f"{serial:>5}" + ln[11:])
        serial += 1
    f.write("END\n")

n_res = len({(l[21], int(l[22:26])) for l in kept})
print(f"cleaned {raw} -> {out}: chain {chain}, {n_res} residues, "
      f"{serial - 1} atoms{tag}")
PY
}

# -------------------------------------------------------------------------
# VHH framework — NbBCII10 nanobody (RFantibody canonical, already cleaned)
# -------------------------------------------------------------------------
if [[ -s "inputs/vhh_nbbcII10.pdb" ]]; then
  echo "have inputs/vhh_nbbcII10.pdb  (VHH framework)"
else
  if [[ -f "$RFAB_SRC/h-NbBCII10.pdb" ]]; then
    cp "$RFAB_SRC/h-NbBCII10.pdb" "inputs/vhh_nbbcII10.pdb"
    echo "copied h-NbBCII10.pdb from RFantibody repo (canonical VHH framework, chain H)"
  else
    echo "MISSING VHH framework — RFantibody repo not found"
    exit 1
  fi
fi

# -------------------------------------------------------------------------
# scFv framework — humanized hu-4D5-8-Fv (RFantibody canonical, already cleaned)
# -------------------------------------------------------------------------
if [[ -s "inputs/hu-4D5-8_Fv.pdb" ]]; then
  echo "have inputs/hu-4D5-8_Fv.pdb  (scFv framework)"
else
  if [[ -f "$RFAB_SRC/hu-4D5-8_Fv.pdb" ]]; then
    cp "$RFAB_SRC/hu-4D5-8_Fv.pdb" "inputs/hu-4D5-8_Fv.pdb"
    echo "copied hu-4D5-8_Fv.pdb from RFantibody repo"
  else
    echo "MISSING scFv framework — RFantibody repo not found"
    exit 1
  fi
fi

# -------------------------------------------------------------------------
# RFantibody-authored pre-processed targets (already epitope-cropped upstream)
# -------------------------------------------------------------------------
if [[ -s "inputs/rsv_site3.pdb" ]]; then
  echo "have inputs/rsv_site3.pdb  (RSV Site III, pre-processed)"
else
  cp "$RFAB_SRC/rsv_site3.pdb" "inputs/rsv_site3.pdb"
  echo "copied rsv_site3.pdb from RFantibody repo"
fi

if [[ -s "inputs/flu_HA.pdb" ]]; then
  echo "have inputs/flu_HA.pdb  (Influenza HA, pre-processed)"
else
  cp "$RFAB_SRC/flu_HA.pdb" "inputs/flu_HA.pdb"
  echo "copied flu_HA.pdb from RFantibody repo"
fi

# -------------------------------------------------------------------------
# Download + clean RCSB targets.
# Chain letter is the leading char of each entry's hotspots in config.py.
# -------------------------------------------------------------------------
dl_pdb "2NY7" "HIV Env"
clean_target "2NY7" "G" "G371,G375,G435,G475"

dl_pdb "6M0J" "SARS-CoV-2 RBD"
clean_target "6M0J" "E" "E492,E493,E494,E495,E496,E497"

dl_pdb "7LVW" "RSV-F Site I"
clean_target "7LVW" "D" "D469,D384"

dl_pdb "6C0B" "TcdB"
clean_target "6C0B" "A" "A1433,A1435,A1437,A1438,A1493"

dl_pdb "3DI3" "IL-7Rα"
clean_target "3DI3" "B" "B81,B139,B192"

dl_pdb "7ML7" "TcdB (scFv unique pairing)"
clean_target "7ML7" "A" "A1816,A1818,A1819,A1823,A1831"

echo ""
echo "done. inputs in ./inputs/ (raw preserved in ./inputs/raw/):"
ls -1 inputs/
