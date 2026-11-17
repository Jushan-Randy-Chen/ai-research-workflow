"""Publication figures: one style, vector + raster export, and a content hash for the verification gates.

    import matplotlib.pyplot as plt
    from airesearch import figures
    figures.use_style()
    fig, ax = plt.subplots(figsize=figures.size("column"))
    ...
    info = figures.save(fig, "runs/figures/toy_regret")   # writes .pdf and .png, returns paths + sha256

The verification gate (`research-loop`) reviews the exact bytes a paper includes, so regenerate figures only through
scripts, never by hand-editing exported files.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from airesearch.provenance import sha256_file  # noqa: E402

# Okabe-Ito: distinguishable for colour-blind readers and in greyscale when paired with line styles.
PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9", "#F0E442", "#000000"]
LINESTYLES = ["-", "--", "-.", ":", (0, (5, 1.5, 1, 1.5)), (0, (1, 1))]
WIDTHS_IN = {"column": 3.25, "text": 6.75}      # ICML/NeurIPS-style single column and full text width


def size(width: str = "column", aspect: float = 0.68) -> tuple[float, float]:
    w = WIDTHS_IN[width]
    return w, w * aspect


def use_style() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif", "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
        "legend.fontsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7,
        "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
        "axes.prop_cycle": plt.cycler(color=PALETTE[:6]) + plt.cycler(linestyle=LINESTYLES),
        "pdf.fonttype": 42, "ps.fonttype": 42,      # embed TrueType fonts (camera-ready requirement)
        "savefig.bbox": "tight", "savefig.dpi": 300,
    })


def save(fig, stem: str | Path) -> dict:
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    out = {}
    for ext in ("pdf", "png"):
        path = stem.with_suffix("." + ext)
        fig.savefig(path, metadata={"CreationDate": None} if ext == "pdf" else None)
        out[ext] = {"path": str(path), "sha256": sha256_file(path)}
    plt.close(fig)
    return out
