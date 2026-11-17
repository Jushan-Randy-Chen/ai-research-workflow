import numpy as np
import pytest

from airesearch import stats


def test_iqm_drops_outer_quartiles():
    assert stats.iqm([0, 1, 2, 3, 4, 5, 6, 100]) == pytest.approx(np.mean([2, 3, 4, 5]))


def test_bootstrap_ci_contains_mean_and_is_reproducible():
    x = np.random.default_rng(1).normal(3.0, 1.0, size=50)
    a, b = stats.bootstrap_ci(x, rng=0), stats.bootstrap_ci(x, rng=0)
    assert a == b and a.low < x.mean() < a.high and a.n == 50


def test_paired_difference_removes_shared_noise():
    rng = np.random.default_rng(0)
    shared = rng.normal(0, 10, size=20)                  # large per-seed noise shared by both methods
    a, b = shared + 1.0, shared + rng.normal(0, 0.1, size=20)
    assert stats.paired_difference(a, b).excludes(0.0)
    with pytest.raises(ValueError):
        stats.paired_difference(a, b[:5])


def test_stratified_bootstrap_shape_check():
    s = np.random.default_rng(0).uniform(size=(5, 4))
    ci = stats.stratified_bootstrap(s, n_boot=200)
    assert ci.low <= ci.estimate <= ci.high
    with pytest.raises(ValueError):
        stats.stratified_bootstrap(s.ravel())
