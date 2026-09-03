#!/usr/bin/env python3
"""Convert a UTF-8 BibTeX database into bibtex-safe ASCII.

Native BibTeX (the .bst engine driving oup-abbrvnat.bst) is not Unicode-aware:
its internal `change.case$` / `format.name$` routines corrupt multi-byte UTF-8
sequences (e.g. accented initials in author lists), which then surface as
``LaTeX Error: Invalid UTF-8 byte sequence`` when the generated .bbl is read
back by pdfLaTeX. The standard fix is to turn the master UTF-8 .bib into an
ASCII, LaTeX-accent-escaped database before BibTeX sees it.

This script rewrites every non-ASCII character into its LaTeX accent command
(e.g. "é" -> "{\\'e}", "Ł" -> "{\\L}"). It never edits the committed master
``references.bib``; build.sh uses it to emit a derived ``references-escaped.bib``.

Exit status is non-zero if any non-ASCII character has no mapping, so a future
Zotero re-export that introduces a new glyph fails loudly instead of being
silently mangled.
"""
import sys

MAP = {
    # spaces / punctuation
    "\u00a0": " ",      # no-break space -> ordinary space
    "\u2013": "--",     # en dash
    "\u2014": "---",    # em dash
    "\u2018": "`",      # left single quote
    "\u2019": "'",      # right single quote
    "\u201c": "``",     # left double quote
    "\u201d": "''",     # right double quote
    # Latin letters with accents / diacritics (covers the bioq Zotero export)
    "á": "{\\'a}", "Á": "{\\'A}",
    "à": "{\\`a}", "À": "{\\`A}",
    "â": "{\\^a}", "Â": "{\\^A}",
    "ä": '{\\"a}', "Ä": '{\\"A}',
    "ã": "{\\~a}", "Ã": "{\\~A}",
    "å": "{\\aa}", "Å": "{\\AA}",
    "é": "{\\'e}", "É": "{\\'E}",
    "è": "{\\`e}", "È": "{\\`E}",
    "ê": "{\\^e}", "Ê": "{\\^E}",
    "ë": '{\\"e}', "Ë": '{\\"E}',
    "ė": "\\.{e}", "Ė": "\\.{E}",
    "í": "{\\'i}", "Í": "{\\'I}",
    "ì": "{\\`i}", "Ì": "{\\`I}",
    "î": "{\\^i}", "Î": "{\\^I}",
    "ï": '{\\"i}', "Ï": '{\\"I}',
    "ó": "{\\'o}", "Ó": "{\\'O}",
    "ò": "{\\`o}", "Ò": "{\\`O}",
    "ô": "{\\^o}", "Ô": "{\\^O}",
    "ö": '{\\"o}', "Ö": '{\\"O}',
    "ú": "{\\'u}", "Ú": "{\\'U}",
    "ù": "{\\`u}", "Ù": "{\\`U}",
    "û": "{\\^u}", "Û": "{\\^U}",
    "ü": '{\\"u}', "Ü": '{\\"U}',
    "ý": "{\\'y}", "Ý": "{\\'Y}",
    "ñ": "{\\~n}", "Ñ": "{\\~N}",
    "ç": "{\\c c}", "Ç": "{\\c C}",
    "ø": "{\\o}", "Ø": "{\\O}",
    "ł": "{\\l}", "Ł": "{\\L}",
    "š": "{\\v{s}}", "Š": "{\\v{S}}",
    "ž": "{\\v{z}}", "Ž": "{\\v{Z}}",
    "ř": "{\\v{r}}", "Ř": "{\\v{R}}",
    "č": "{\\v{c}}", "Č": "{\\v{C}}",
}


def escape(text: str) -> str:
    out = []
    for ch in text:
        if ord(ch) < 128:
            out.append(ch)
        elif ch in MAP:
            out.append(MAP[ch])
        else:
            sys.stderr.write(
                f"escape_bib: unmapped non-ASCII character U+{ord(ch):04X} ({ch!r})\n"
            )
            sys.exit(2)
    return "".join(out)


def main(argv):
    if len(argv) != 3:
        sys.stderr.write("usage: escape_bib.py <input.bib> <output.bib>\n")
        return 1
    src, dst = argv[1], argv[2]
    with open(src, encoding="utf-8") as f:
        data = f.read()
    escaped = escape(data)
    try:
        escaped.encode("ascii")
    except UnicodeEncodeError as e:
        sys.stderr.write(f"escape_bib: output is not ASCII: {e}\n")
        return 1
    with open(dst, "w", encoding="ascii") as f:
        f.write(escaped)
    print(f"[escape_bib] wrote ASCII LaTeX-escaped {dst} <- {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))