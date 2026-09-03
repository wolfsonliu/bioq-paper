#!/usr/bin/env python3
"""Dependency sub-analysis — plot compatibility analysis results as PDF figures.

Reads ``conflict_matrix.csv``, ``pairwise_compat.csv``, and
``package_fragmentation.csv`` (produced by ``analyze_compat.py``) and generates
publication-quality PDF figures.

Figures produced:
  compat_heatmap.pdf          — conflict matrix (n_hard), services × services
  coinstall_heatmap.pdf       — binary co-installability matrix
  package_fragmentation.pdf   — top conflict-driving packages (horizontal bars)

Styling follows ``docs/plotting-style-guide.md``: the bioq brand palette, a
left-aligned ``TEAL_DARK`` panel title, tinted ``BG`` axes, soft grid, no legend
border, and PDF as the archival format. Two figure-specific conventions are used:

- **Conflict intensity** maps through white → ``AMBER`` (pain point) → ``RED``
  (failure), and a `PowerNorm(gamma=0.5)` spreads the heavily-skewed counts
  (91 % of non-zero cells are 1–4, with a tail to 38) so the structure stays
  legible. The colorbar still reads in *actual* package counts.
- **Co-installability** is binary semantic color: ``GREEN`` (PASS = can share a
  venv) vs light ``GREY`` (muted = cannot), so the rare compatible pairs pop.

Usage:
    python3 plot_compat.py                                     # frozen -> figures/frozen/
    python3 plot_compat.py --data-dir data/declared \
        --out-dir figures/declared                             # declared view
    python3 plot_compat.py --data-dir path/to/data \
        --out-dir path/to/figures                              # general form
    python3 plot_compat.py --figsize 14 12 --dpi 200

Requires: matplotlib, pandas, numpy (``uv run --with matplotlib,pandas,numpy``).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless — no DISPLAY needed
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, PowerNorm
from matplotlib.patches import Patch

HERE = Path(__file__).resolve().parent

# --- Brand palette (docs/plotting-style-guide.md §1.1) ---
TEAL_DARK = "#05668D"
TEAL      = "#028090"
GREEN     = "#02C39A"
AMBER     = "#F0A202"
BG        = "#E8F6F3"
RED       = "#C1361D"
GREY      = "#9AA7AD"
PURPLE    = "#7B2D8E"
BLUE      = "#2E86AB"
ORANGE    = "#E76F51"

# --- Typography (guide §2) ---
TITLE_FS  = 13
LABEL_FS  = 11
TICK_FS   = 8
LEGEND_FS = 8
TILE_FS   = 7
SUBSET_FS = 8


def _lighten(hex_color: str, factor: float) -> str:
    """Blend a hex color toward white; factor 0 = original, 1 = white."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


# "Cannot share a venv" tile for the co-installability matrix: a muted, light
# grey (muted/inactive per guide §1.1) — distinct enough from the white grid
# lines to stay legible, but quiet so the rare GREEN "compatible" tiles pop.
COINSTALL_NO = _lighten(GREY, 0.6)


def _trim_label(s: str) -> str:
    """Strip '-server' suffix for compact display labels."""
    return s.removesuffix("-server")


def style_axes(ax, title: str | None = None, *, grid_axis: str | None = None,
               grid_which: str = "both") -> None:
    """Apply the signature panel grammar (guide §3)."""
    ax.set_facecolor(BG)
    if grid_axis:
        ax.grid(True, alpha=0.3, axis=grid_axis)
    else:
        ax.grid(True, alpha=0.3, which=grid_which)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GREY)
    if title:
        ax.set_title(title, color=TEAL_DARK, fontsize=TITLE_FS,
                     fontweight="bold", loc="left")


def style_heatmap(ax, title: str, labels: list[str]) -> None:
    """Style a services×services heatmap (brand title + clean ticks)."""
    ax.set_title(title, color=TEAL_DARK, fontsize=TITLE_FS,
                 fontweight="bold", loc="left", pad=14)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position("top")
    n = len(labels)
    # ha="left" anchors the label's start at the tick and lets it extend
    # up-right (45°) / straight up (90°), keeping the text clear of the top
    # row of cells. ha="center"/"right" would straddle the top edge and
    # overlap the heatmap.
    if n >= 24:  # vertical labels when the matrix is wide
        plt.setp(ax.get_xticklabels(), rotation=90, ha="left",
                 rotation_mode="anchor", fontsize=TILE_FS)
    else:
        plt.setp(ax.get_xticklabels(), rotation=45, ha="left",
                 rotation_mode="anchor", fontsize=TILE_FS)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=TILE_FS)
    ax.tick_params(which="both", length=0)


def draw_heatmap(ax, mat: np.ndarray, labels: list[str], cmap, *,
                 norm=None, vmin=None, vmax=None):
    """Render a square services×services matrix with faint white cell gridlines."""
    im = ax.imshow(mat, cmap=cmap, norm=norm, vmin=vmin, vmax=vmax,
                   interpolation="nearest", aspect="equal", origin="upper")
    n = len(labels)
    ax.set_xticks(np.arange(n), labels)
    ax.set_yticks(np.arange(n), labels)
    ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.3)
    ax.tick_params(which="minor", length=0)
    return im


def save_fig(fig, out: Path, here: Path, *, dpi: int = 150) -> None:
    """Save as archival PDF and print the path relative to the script (guide §6)."""
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=dpi, bbox_inches="tight", pad_inches=0.15, format="pdf")
    try:
        print(f"  -> {out.relative_to(here)}")
    except ValueError:
        print(f"  -> {out}")
    plt.close(fig)


def read_data(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the three CSV outputs from analyze_compat.py."""
    conflict = pd.read_csv(data_dir / "conflict_matrix.csv", index_col=0)
    pairwise = pd.read_csv(data_dir / "pairwise_compat.csv")
    frag = pd.read_csv(data_dir / "package_fragmentation.csv")
    return conflict, pairwise, frag


def plot_conflict_heatmap(conflict: pd.DataFrame, out: Path,
                          figsize: tuple[float, float], dpi: int) -> None:
    """Services × services heatmap of n_hard conflict counts (pain scale)."""
    svcs = list(conflict.index)
    labels = [_trim_label(s) for s in svcs]

    # Symmetric matrix: conflict may be non-square if the CSV is triangular
    mat = conflict.values.astype(float)
    mat = np.maximum(mat, mat.T)  # max of (i,j) and (j,i); diagonal 0

    vmax = float(max(mat.max(), 1))
    cmap = LinearSegmentedColormap.from_list("conflict", ["#FFFFFF", AMBER, RED])
    # Power scale reveals the skewed low counts (91 % of cells are 1–4) while
    # keeping the heavy tail (up to 38) mapped to RED.
    norm = PowerNorm(gamma=0.5, vmin=0, vmax=vmax)

    fig, ax = plt.subplots(figsize=figsize)
    im = draw_heatmap(ax, mat, labels, cmap, norm=norm)
    style_heatmap(ax, "Conflicts — HARD-incompatible packages per service pair", labels)

    cbar = fig.colorbar(im, ax=ax, shrink=0.75)
    cbar.set_label("HARD-incompatible packages\n(build / major / range)",
                   fontsize=LABEL_FS - 2, color=TEAL_DARK)
    cbar.ax.tick_params(labelsize=TILE_FS)
    cbar.outline.set_visible(False)

    fig.tight_layout()
    save_fig(fig, out, HERE, dpi=dpi)


def plot_coinstall_heatmap(conflict: pd.DataFrame, pairwise: pd.DataFrame,
                           out: Path, figsize: tuple[float, float], dpi: int) -> None:
    """Binary heatmap: green = co-installable as-is, light grey = any conflict."""
    svcs = list(conflict.index)
    labels = [_trim_label(s) for s in svcs]
    n = len(svcs)

    compat_map: dict[tuple[str, str], bool] = {}
    for _, row in pairwise.iterrows():
        a, b = row["service_a"], row["service_b"]
        compat_map[(a, b)] = bool(row["coinstallable"])
        compat_map[(b, a)] = bool(row["coinstallable"])

    mat = np.zeros((n, n), dtype=float)
    for i, a in enumerate(svcs):
        for j, b in enumerate(svcs):
            mat[i, j] = 1.0 if (i == j or compat_map.get((a, b), False)) else 0.0

    fig, ax = plt.subplots(figsize=figsize)
    cmap = LinearSegmentedColormap.from_list(
        "coinstall", [COINSTALL_NO, GREEN], N=2)
    draw_heatmap(ax, mat, labels, cmap, vmin=0, vmax=1)
    style_heatmap(ax, "Co-installability — can two services share one venv?", labels)

    legend_elements = [
        Patch(facecolor=GREEN, label="Co-installable  (PASS)"),
        Patch(facecolor=COINSTALL_NO, label="Incompatible"),
    ]
    ax.legend(handles=legend_elements, loc="lower left", fontsize=LEGEND_FS,
              frameon=False, borderpad=0.6)

    total_pairs = n * (n - 1) // 2
    compat_count = sum(1 for _, r in pairwise.iterrows() if r["coinstallable"])
    pct = 100 * compat_count / total_pairs if total_pairs else 0
    ax.text(0.0, -0.10, f"Co-installable pairs: {compat_count} / {total_pairs}"
             f"  ({pct:.1f} % of pairs)",
            transform=ax.transAxes, ha="left", va="top",
            fontsize=SUBSET_FS, color=TEAL_DARK)

    fig.tight_layout()
    save_fig(fig, out, HERE, dpi=dpi)


def plot_fragmentation(frag: pd.DataFrame, out: Path,
                       figsize: tuple[float, float], dpi: int, top_n: int = 20) -> None:
    """Horizontal bar chart: top-N conflict-driving packages (single hue)."""
    top = (frag[frag["conflicting_pairs"] > 0]
           .sort_values("conflicting_pairs", ascending=False)
           .head(top_n)
           .copy())
    if top.empty:
        print("  fragmentation: no data to plot (all pairs compatible)")
        return

    top = top.sort_values("conflicting_pairs", ascending=True)  # largest on top
    nrows = len(top)
    counts = top["conflicting_pairs"].astype(float).values
    y = np.arange(nrows)

    # Height-proportional rows (guide §8): keeps two-line tick labels readable.
    fig_h = max(4.0, 0.28 * nrows + 1.6)
    fig, ax = plt.subplots(figsize=(figsize[0], fig_h))

    ax.barh(y, counts, color=AMBER, alpha=0.85, edgecolor="white", linewidth=0.5)

    ax.set_yticks(y)
    ax.set_yticklabels(
        [f"{row['package']}\n({int(row['n_versions'])} versions)" for _, row in top.iterrows()],
        fontsize=TILE_FS,
    )
    for yi, c in zip(y, counts):
        ax.text(c + max(counts) * 0.015, yi, f"{int(c)}",
                va="center", ha="left", fontsize=SUBSET_FS, color=TEAL_DARK)

    ax.set_xlabel("Conflicting service pairs", fontsize=LABEL_FS)
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%d"))
    ax.margins(x=0.16)
    style_axes(ax, title=f"Top {nrows} conflict-driving packages", grid_axis="x")

    fig.tight_layout()
    save_fig(fig, out, HERE, dpi=dpi)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-dir", default="",
                    help="dir with conflict_matrix.csv, pairwise_compat.csv, "
                         "package_fragmentation.csv (default: data/frozen/)")
    ap.add_argument("--out-dir", default="",
                    help="output dir for PDF figures (default: figures/frozen/)")
    ap.add_argument("--figsize", nargs=2, type=float, default=(11, 10),
                    help="figure width and height in inches (default: 11 10)")
    ap.add_argument("--dpi", type=int, default=150,
                    help="figure resolution (default: 150)")
    ap.add_argument("--top-n", type=int, default=20,
                    help="top-N packages to show in fragmentation chart (default: 20)")
    args = ap.parse_args()

    data_dir = Path(args.data_dir or str(HERE / "data" / "frozen")).expanduser().resolve()
    out_dir = Path(args.out_dir or str(HERE / "figures" / "frozen")).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    for fname in ("conflict_matrix.csv", "pairwise_compat.csv", "package_fragmentation.csv"):
        if not (data_dir / fname).is_file():
            raise SystemExit(f"required input not found: {data_dir / fname}")

    print(f"reading data from {data_dir}")
    conflict, pairwise, frag = read_data(data_dir)

    n_svcs = len(conflict)
    n_pairs = len(pairwise)
    print(f"  services: {n_svcs}   pairs: {n_pairs}")

    figsize = tuple(args.figsize)
    dpi = args.dpi

    print("generating figures ...")
    plot_conflict_heatmap(conflict, out_dir / "compat_heatmap.pdf", figsize, dpi)
    plot_coinstall_heatmap(conflict, pairwise, out_dir / "coinstall_heatmap.pdf",
                           figsize, dpi)
    plot_fragmentation(frag, out_dir / "package_fragmentation.pdf",
                       (figsize[0], figsize[1]), dpi, args.top_n)

    print(f"\ndone -> figures written under {out_dir}")


if __name__ == "__main__":
    main()
