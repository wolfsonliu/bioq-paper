#!/usr/bin/env bash
# Regenerate the package-level co-installability analysis + figures for BOTH views,
# each into its own clearly separated output directory.
#
#   frozen   -> data/frozen/    + figures/frozen/    (from data/service_dependency/)
#   declared -> data/declared/  + figures/declared/  (from data/repo_dependency/)
#
# The per-service inputs (data/service_dependency/ and data/repo_dependency/) are
# committed, so this script runs fully offline. To regenerate *those* inputs, see
# the "Extraction" steps in the README:
#   - frozen:   python3 extract_deps.py          (needs docker + the built images)
#   - declared: extract_repo_deps.py per repo    (needs the opensource checkouts)
#
# The declared view compares specifier ranges, which needs `packaging`
# (`uv run --with packaging python ...` if it is not already importable).
set -euo pipefail
cd "$(dirname "$0")"

# matplotlib writes a font cache; point its config dir somewhere writable when the
# HOME config dir is read-only (sandboxed/CI contexts), else it falls back to HOME.
export MPLCONFIGDIR="${MPLCONFIGDIR:-${TMPDIR:-/tmp}/mplconfig}"
mkdir -p "$MPLCONFIGDIR"

echo "== [1/4] analyze frozen view (image envs): data/service_dependency -> data/frozen/ =="
python3 analyze_compat.py \
    --dep-dir data/service_dependency \
    --out-dir data/frozen

echo
echo "== [2/4] analyze declared view (repo constraints): data/repo_dependency -> data/declared/ =="
python3 analyze_compat.py \
    --dep-dir data/repo_dependency \
    --out-dir data/declared

echo
echo "== [3/4] plot frozen view: data/frozen -> figures/frozen/ =="
python3 plot_compat.py \
    --data-dir data/frozen \
    --out-dir figures/frozen

echo
echo "== [4/4] plot declared view: data/declared -> figures/declared/ =="
python3 plot_compat.py \
    --data-dir data/declared \
    --out-dir figures/declared

echo
echo "done."
echo "  analysis : data/frozen/{pairwise_compat,conflict_matrix,package_fragmentation}.csv (frozen)"
echo "             data/declared/{...} (declared)"
echo "  figures  : figures/frozen/*.pdf (frozen)  +  figures/declared/*.pdf (declared)"