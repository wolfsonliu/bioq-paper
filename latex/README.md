# paper-bioinformatics/latex — OUP authoring-template LaTeX build

LaTeX source for the bioq *Bioinformatics* (Applications Note) draft, converted
from `../manuscript.md` using the OUP authoring template that ships in
`materials/bioinformatics/`. This directory is **private draft material** (it
sits outside the public `paper/` subtree), like its `../manuscript.md` parent.

## Files

| File | Role |
|------|------|
| `manuscript.tex` | The main text (title, abstract, §1–§5, Figure 1, references). Source of truth for the PDF *render*; the markdown `../manuscript.md` remains the source of truth for content. |
| `supplementary.tex` | Standalone supplementary material (Figures S1–S9 + Table S1/S2 stubs + the fleet citations) compiled into its own PDF. Uses plain `article` (not the OUP template) — see below. |
| `build.sh` | One-shot build: derives the bib, then compiles both documents (`pdflatex → bibtex → pdflatex×n` until cross-references settle) and reports warnings. |
| `escape_bib.py` | Build helper: rewrites the committed master `references.bib` (UTF-8) into a bibtex-safe ASCII `references-escaped.bib`. Never edits the master. |
| `oup-authoring-template.cls` | OUP document class (copied from `materials/bioinformatics/oup-authoring-template/`). |
| `oup-abbrvnat.bst` / `oup-plain.bst` | Author–year / numbered bibliography styles (copied from the same bundle). |
| `oup-abbrvnat-et-al.bst` | Derived from `oup-abbrvnat.bst`: truncates long author lists in the reference list to 6 + "et al." (see the `#6` in its `format.names`; current `\bibliographystyle` for both `.tex` files). |
| `OUP-TEMPLATE-*.txt` | Provenance (`README` + `manifest.txt`) of the OUP bundle. |
| `texmf-local/` | Vendored LPPL packages the class hard-depends on (see below). |
| `references.bib` | The committed Zotero/Better-BibTeX master (UTF-8); never hand-edit. |
| `references-escaped.bib` | **Generated at build time** from `references.bib`; bibtex-safe ASCII; do not hand-edit or commit. |
| `build/`, `*.{aux,log,bbl,blg,out,pdf,toc,...}` | Build artifacts; regenerate with `build.sh`. |

## Build

```bash
cd paper-bioinformatics/latex
./build.sh          # -> manuscript.pdf + supplementary.pdf
```

Prerequisites: `pdflatex`, `bibtex`, and `python3` on `PATH`. A full TeX Live
(≥ 2020) is ideal; the few packages `oup-authoring-template.cls` needs that a
minimal install may lack (`totcount`, `algorithmicx`, `subfloat`, `anyfontsize`)
are vendored under `texmf-local/` and are pulled in automatically only when the
local TeX Live does not provide them.

## Bibliography workflow (do not break this)

- The single source of truth is `references.bib` (the Zotero/Better-BibTeX
  export, committed to this repository). It is **never edited** here.
- `build.sh` runs `escape_bib.py references.bib references-escaped.bib` to
  derive a bibtex-safe copy. The escaping exists because **native BibTeX is not
  Unicode-aware**: its `change.case$`/`format.name$` routines corrupt multi-byte
  UTF-8 in author lists (e.g. accented initials), producing
  "Invalid UTF-8 byte sequence" errors on the next pass. `\citep{}` keys are
  stable Zotero keys and are unaffected.

## Template choices (change centrally if needed)

- `manuscript.tex` uses the OUP class with `webpdf,contemporary,large,namedate`.
  `namedate` selects author–year citations (natbib + `oup-abbrvnat.bst`),
  matching the author–date CSL used for the Word render; drop it and use
  `oup-plain.bst` for numbered citations. Sections are numbered because
  `unnumsec` is omitted.
- `supplementary.tex` deliberately does **not** use the OUP template:
  supplementary material is a plain, separately-uploaded PDF, not journal-copy,
  so it uses standard `article` + `geometry` + `natbib` (`authoryear,round`) and
  keeps `oup-abbrvnat-et-al.bst` purely so its reference list reads like the main
  text's. It needs **no** vendored packages.
- Reference-list author truncation: both documents use the derived
  `oup-abbrvnat-et-al.bst`, which prints the first **6** authors then "et al.".
  To change the number, edit the `#6` in `FUNCTION {format.names}` in that `.bst`
  (there is no LaTeX-level switch; `natbib` does not expose one). In-text `\citep`
  already shows "First Author et al." regardless.
- Fonts (both): `\usepackage[T1]{fontenc}` + `textcomp` so literal `<`, `>` and
  textcomp glyphs typeset without changing the layout.
- Figure 1 is a full-width `figure*` float in `manuscript.tex`; the supplementary
  figures are full-width single-column floats in `supplementary.tex`, whose
  figure counter is redefined to `S#` so the main text's inline
  "Figure S1"–"S9" stay correct.

## Main text vs supplementary split

- `manuscript.tex` holds only the application-note body: title/abstract,
  §1 Introduction … §5 Discussion, the full-width **Figure 1**, and the ~22
  references the main text actually cites. It renders to ≈5 pages.
- `supplementary.tex` holds everything readers see "Supplementary": **Figures
  S1–S9** (full-width, captioned, numbered `S1…S9`), the **Table S1 / S2** stubs,
  and the fleet-method citations (which keeps every `references.bib` entry
  resolvable without bloating the main bibliography). It renders to ≈9 pages of
  single-column `article` output.
- Both share `references.bib`, the figure assets, and `escape_bib.py`; they
  differ in class (OUP vs `article`). `build.sh` builds them in one pass.

## Known benign warnings (this TeX Live, `manuscript.tex` only)

- `Unused global option(s): [webpdf,contemporary,large,namedate]` — a cosmetic
  OUP-class quirk (the class consumes the options; they are also left in the
  global list seen by `\AtBeginDocument`-loaded packages). Output is correct.
- `You have requested release '2026/06/01' ...` — the class declares a
  marginally newer kernel requirement than the installed one; harmless.
- `Text page N contains only floats` — expected when the full-width Figure 1
  lands on its own page in two-column mode.

(`supplementary.tex` builds warning-free, since `article` avoids the OUP class
quirks above.)

## Open stubs (mirrors `../manuscript.md` and `../figures/FIGURES.md`)

- `TODO:` placeholders in the `.tex` front matter (authors, address, contact),
  §4.1 (VRAM minima), §4.2 (E2 parity), §4.5 (E6b scope note), and the
  supplementary-table sections (Table 1, S1, S2). Clear every `TODO` before
  submission.
- `references.bib` still contains a few date-less entries (`*_nodate` keys);
  they render without a year in the LaTeX path (the Word render shows "n.d.").
- The draft already splits main text (`manuscript.pdf`, ≈5 pages) from the
  supplementary material (`supplementary.pdf`, ≈9 pages). To hit the ~4-page
  Applications Note budget, tighten the main-text prose and dump the full fleet
  table into `supplementary.tex` as planned.