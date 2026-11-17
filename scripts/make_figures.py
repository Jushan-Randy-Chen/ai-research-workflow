"""Figures for the worked example: cumulative regret by step, mean over seeds with a 95% bootstrap band.

    uv run python scripts/make_figures.py            # writes runs/figures/toy_regret.{pdf,png}
    cp runs/figures/toy_regret.pdf paper/figures/    # only after the visual review (research-loop record-visual)

Reads only saved results; never re-runs experiments.
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np

from airesearch import figures, stats
from airesearch.experiments.toy_bandit import AGENTS
from airesearch.provenance import ROOT

LABELS = {"thompson": "Thompson (ours)", "greedy": "Greedy (posterior mean)", "eps_greedy": r"$\epsilon$-greedy",
          "thompson_shared_noise": "Thompson, shared noise (ablation)"}


def load(agent: str) -> np.ndarray:
    files = sorted((ROOT / "runs/toy_bandit").glob(f"{agent}_seed*/result.json"))
    return np.array([json.loads(f.read_text())["cumulative_regret"] for f in files])


def main() -> None:
    figures.use_style()
    fig, ax = plt.subplots(figsize=figures.size("column"))
    summary = {}
    for agent in AGENTS:
        curves = load(agent)                                   # (seeds, steps)
        if len(curves) < 2:
            continue
        x = np.arange(1, curves.shape[1] + 1)
        idx = np.random.default_rng(0).integers(0, len(curves), size=(2000, len(curves)))
        lo, hi = np.percentile(curves[idx].mean(axis=1), [2.5, 97.5], axis=0)
        ax.plot(x, curves.mean(axis=0), label=LABELS[agent])
        ax.fill_between(x, lo, hi, alpha=0.2, linewidth=0)
        summary[agent] = str(stats.bootstrap_ci(curves[:, -1]))
    ax.set_xlabel("step")
    ax.set_ylabel("cumulative regret")
    # Legend above the axes: inside, it covered the right-hand bands (found in the visual review).
    fig.legend(loc="lower center", bbox_to_anchor=(0.5, 0.98), ncol=2)
    info = figures.save(fig, ROOT / "runs/figures/toy_regret")
    print(json.dumps({"figure": info, "final_regret": summary}, indent=1))


if __name__ == "__main__":
    main()
