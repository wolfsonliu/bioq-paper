#!/usr/bin/env bash
#
# Build the bioq Bioinformatics (Applications Note) LaTeX sources into PDFs:
#   manuscript.pdf     -- the ~4-page main text (Figure 1 + references)
#   supplementary.pdf  -- the supplementary figures S1--S9 and tables (separate)
# It also emits PostScript copies of each PDF (manuscript.ps, supplementary.ps)
# via Ghostscript's pdf2ps when that tool is available, and combines the two
# PDFs into a single manuscript-combined.pdf (main text + supplementary).
#
# Prerequisites: a standard TeX Live (>= 2020) with pdflatex + bibtex + the usual
# OUP class dependencies. The few packages oup-authoring-template.cls needs
# (totcount, algorithmicx, subfloat, anyfontsize) are vendored under
# ./texmf-local/ as a fallback and are used automatically only when the local TeX
# Live lacks them, so this works on both full and minimal installs.
#
# The bibliography is the committed, Zotero-exported master ./references.bib
# (UTF-8; never hand-edited). build.sh derives a bibtex-safe ASCII copy,
# `references-escaped.bib`, from it at build time. Only that derived file is fed
# to BibTeX, so it is not committed.
#
set -euo pipefail
cd "$(dirname "$0")"

MAINS="manuscript supplementary"
BIB_SRC="./references.bib"
ESC_BIB="references-escaped.bib"
LOGDIR="build"

mkdir -p "$LOGDIR"

# --- 1. Derive a bibtex-safe bibliography from the committed master.
#      escape_bib.py turns non-ASCII into LaTeX escapes (native BibTeX corrupts
#      multi-byte UTF-8), leaving ./references.bib untouched. The .tex files
#      cite `references-escaped`.
if [ -f "$BIB_SRC" ]; then
  python3 escape_bib.py "$BIB_SRC" "$ESC_BIB"
else
  echo "[build] WARNING: $BIB_SRC not found; reusing any existing $ESC_BIB" >&2
fi

# --- 2. Fall back to locally vendored packages when the TeX Live install lacks
#        a \RequirePackage dependency of oup-authoring-template.cls.
missing=0
for pkg in totcount.sty algorithmicx.sty algpseudocode.sty subfloat.sty anyfontsize.sty; do
  if ! kpsewhich "$pkg" >/dev/null 2>&1; then missing=1; fi
done
if [ "$missing" -eq 1 ]; then
  export TEXINPUTS="./texmf-local//:${TEXINPUTS:-}"
  echo "[build] prepending ./texmf-local// (system TeX Live is missing class dependencies)"
fi

# --- 3. Compile each document: pdflatex -> bibtex -> pdflatex (until settled).
run_pdflatex() {  # $1 = main name
  pdflatex -interaction=nonstopmode -file-line-error "$1.tex" \
    > "$LOGDIR/$1-pdflatex.log" 2>&1
}

for MAIN in $MAINS; do
  echo "==== [build] $MAIN ===="

  echo "[build] pdflatex (initial pass)"
  if ! run_pdflatex "$MAIN"; then
    echo "!! pdflatex failed (initial); tail of log:" >&2
    tail -n 60 "$LOGDIR/$MAIN-pdflatex.log" >&2
    exit 1
  fi

  echo "[build] bibtex"
  if ! bibtex "$MAIN" > "$LOGDIR/$MAIN-bibtex.log" 2>&1; then
    echo "!! bibtex failed; tail of log:" >&2
    tail -n 60 "$LOGDIR/$MAIN-bibtex.log" >&2
    cat "$MAIN.blg" >&2 2>/dev/null || true
    exit 1
  fi

  # Re-run pdflatex until citations/cross-references settle (capped at 5 passes).
  settled=0
  for i in 1 2 3 4 5; do
    echo "[build] pdflatex (settle pass $i)"
    if ! run_pdflatex "$MAIN"; then
      echo "!! pdflatex failed (pass $i); tail of log:" >&2
      tail -n 60 "$LOGDIR/$MAIN-pdflatex.log" >&2
      exit 1
    fi
    if ! grep -aqE 'Rerun to get cross-references right|Label\(s\) may have changed|Citation\(s\) may have changed' \
         "$LOGDIR/$MAIN-pdflatex.log"; then
      settled=1
      break
    fi
  done
  if [ "$settled" -ne 1 ]; then
    echo "[build] WARNING: cross-references did not fully settle after 5 passes" >&2
  fi
done

# --- 4. Emit PostScript copies (.ps) via Ghostscript. Optional: skipped with a
#        warning when pdf2ps is not installed; a conversion failure is non-fatal.
if command -v pdf2ps >/dev/null 2>&1; then
  for MAIN in $MAINS; do
    echo "[build] pdf2ps -> $MAIN.ps"
    if ! pdf2ps "$MAIN.pdf" "$MAIN.ps"; then
      echo "[build] WARNING: pdf2ps failed for $MAIN.pdf; no $MAIN.ps produced" >&2
    fi
  done
else
  echo "[build] WARNING: pdf2ps (Ghostscript) not found; skipping .ps output" >&2
fi

# --- 5. Combine manuscript.pdf + supplementary.pdf into a single PDF.
COMBINED="manuscript-combined.pdf"
if [ -f "manuscript.pdf" ] && [ -f "supplementary.pdf" ]; then
  if command -v pdfunite >/dev/null 2>&1; then
    echo "[build] pdfunite -> $COMBINED"
    if ! pdfunite manuscript.pdf supplementary.pdf "$COMBINED"; then
      echo "[build] WARNING: pdfunite failed; no $COMBINED produced" >&2
    fi
  elif command -v gs >/dev/null 2>&1; then
    echo "[build] gs (pdfwrite) -> $COMBINED"
    if ! gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile="$COMBINED" \
         manuscript.pdf supplementary.pdf; then
      echo "[build] WARNING: gs failed; no $COMBINED produced" >&2
    fi
  else
    echo "[build] WARNING: no pdfunite/gs available; skipping $COMBINED" >&2
  fi
else
  echo "[build] WARNING: manuscript.pdf and/or supplementary.pdf missing; skipping $COMBINED" >&2
fi

# --- 6. Report.
rc=0
for MAIN in $MAINS; do
  if [ -f "$MAIN.pdf" ]; then
    pages=$(pdfinfo "$MAIN.pdf" 2>/dev/null | awk '/^Pages/{print $2}')
    echo "[build] OK -> $MAIN.pdf ($(stat -c%s "$MAIN.pdf" 2>/dev/null || wc -c < "$MAIN.pdf") bytes, $pages pages)"
    if [ -f "$MAIN.ps" ]; then
      echo "[build] OK -> $MAIN.ps ($(stat -c%s "$MAIN.ps" 2>/dev/null || wc -c < "$MAIN.ps") bytes)"
    fi
    echo "[build] $MAIN warnings:"
    grep -aE '^LaTeX Warning:|^Package .* Warning:|Undefined|Citation .* undefined|Reference .* undefined|There were (undefined references|multiply-defined labels)' \
      "$LOGDIR/$MAIN-pdflatex.log" | sort -u | head -n 40 || true
  else
    echo "[build] FAILED: $MAIN.pdf was not produced" >&2
    rc=1
  fi
done
if [ -f "$COMBINED" ]; then
  cpages=$(pdfinfo "$COMBINED" 2>/dev/null | awk '/^Pages/{print $2}')
  echo "[build] OK -> $COMBINED ($(stat -c%s "$COMBINED" 2>/dev/null || wc -c < "$COMBINED") bytes, $cpages pages)"
else
  echo "[build] (no combined PDF $COMBINED)"
fi
exit $rc
