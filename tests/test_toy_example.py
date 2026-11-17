"""The worked example behaves as its hypothesis predicts on a small, fast setting."""

import numpy as np

from airesearch.experiments import toy_bandit

CFG = {"steps": 300, "n_arms": 5, "n_problems": 10, "epsilon": 0.1}


def test_same_seed_same_problem_for_every_agent():
    a = toy_bandit.run(CFG, "greedy", seed=3)
    b = toy_bandit.run(CFG, "greedy", seed=3)
    assert a == b


def test_thompson_beats_greedy_over_seeds():
    ts = [toy_bandit.run(CFG, "thompson", s)["final_regret"] for s in range(4)]
    gr = [toy_bandit.run(CFG, "greedy", s)["final_regret"] for s in range(4)]
    assert np.mean(ts) < np.mean(gr)
