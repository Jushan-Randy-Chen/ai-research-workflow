"""Worked example: does posterior sampling explore better than acting greedily on the posterior mean?

Hypothesis (docs/PROJECT.md): on Bernoulli bandits, Thompson sampling (sample a mean per arm from the Beta posterior,
play the argmax) has lower cumulative regret than the greedy agent (argmax of the posterior MEAN), because greedy can
lock onto a sub-optimal arm.
  method    thompson
  baseline  greedy, eps_greedy (epsilon 0.1)
  ablation  thompson_shared_noise: one shared Beta draw quantile for all arms per step (isolates "independent
            per-arm randomness"; everything else identical)

What the example shows (5 seeds, 500 steps, paired over seeds; `make example` prints these):
  greedy - thompson        +8.5 regret [0.9, 15.7]   (supports H1, but wide: greedy locks on in 3 of 5 seeds)
  eps_greedy - thompson   +11.9 regret [7.7, 16.7]
  shared_noise - thompson  -4.8 regret [-6.8, -2.6]  (the ablation does NOT support the guess behind it)
So independent per-arm noise is not the ingredient that matters here. Our explanation (inferred, not measured): one
shared quantile per step acts like an optimistic index, close to Bayes-UCB. An ablation is worth running exactly when
its answer is not known in advance; record such a result honestly. With n = 5 the percentile bootstrap is coarse;
use more seeds before claiming anything.

Tiny and numpy-only on purpose: it runs in seconds and exercises config -> seeded runs -> stats -> figure -> gates.
"""

from __future__ import annotations

import numpy as np

AGENTS = ("thompson", "greedy", "eps_greedy", "thompson_shared_noise")


def make_problem(n_arms: int, rng: np.random.Generator) -> np.ndarray:
    return rng.uniform(0.05, 0.95, size=n_arms)


def choose(agent: str, wins: np.ndarray, losses: np.ndarray, rng: np.random.Generator, epsilon: float) -> int:
    a, b = wins + 1.0, losses + 1.0                       # Beta(1, 1) prior
    if agent == "thompson":
        return int(np.argmax(rng.beta(a, b)))
    if agent == "thompson_shared_noise":
        u = rng.uniform()                                 # one quantile for all arms (correlated draws)
        draws = np.array([np.quantile(rng.beta(ai, bi, size=64), u) for ai, bi in zip(a, b, strict=True)])
        return int(np.argmax(draws))
    if agent == "eps_greedy" and rng.uniform() < epsilon:
        return int(rng.integers(len(a)))
    if agent in ("greedy", "eps_greedy"):
        mean = a / (a + b)
        return int(rng.choice(np.flatnonzero(mean == mean.max())))
    raise ValueError(f"unknown agent {agent!r}; choose from {AGENTS}")


def run(config: dict, agent: str, seed: int, log=None) -> dict:
    """One seeded run: the problem instance depends only on the seed, so every agent faces the same bandits."""
    env_rng = np.random.default_rng([seed, 0])
    agent_rng = np.random.default_rng([seed, 1, AGENTS.index(agent)])
    steps, n_arms, n_problems = config["steps"], config["n_arms"], config["n_problems"]
    regret = np.zeros((n_problems, steps))
    for k in range(n_problems):
        p = make_problem(n_arms, env_rng)
        wins, losses = np.zeros(n_arms), np.zeros(n_arms)
        for t in range(steps):
            arm = choose(agent, wins, losses, agent_rng, config["epsilon"])
            reward = env_rng.uniform() < p[arm]
            wins[arm] += reward
            losses[arm] += 1 - reward
            regret[k, t] = p.max() - p[arm]
    cumulative = regret.cumsum(axis=1).mean(axis=0)
    if log is not None:
        for t in range(0, steps, max(1, steps // 10)):
            log(step=t, cumulative_regret=float(cumulative[t]))
    return {"final_regret": float(cumulative[-1]), "cumulative_regret": cumulative.tolist()}


def check_results(loop) -> list[tuple]:
    """Project-specific result check, registered in docs/research_loop/registry.json under result_checks."""
    import json
    rows = []
    for agent in AGENTS:
        files = sorted(loop.root.glob(f"runs/toy_bandit/{agent}_seed*/result.json"))
        values = [json.loads(f.read_text())["final_regret"] for f in files]
        bad = [v for v in values if not np.isfinite(v) or v < 0]
        state = "FAIL" if bad else ("OK" if len(values) >= 5 else "MISSING")
        rows.append((f"toy_bandit {agent}", state, f"{len(values)} seeds; regret must be finite and >= 0"))
    return rows
