"""Statistics for small numbers of seeds/instances (the usual situation in ML papers).

Rules of thumb encoded here (see docs/PROTOCOL.md):
  * report a confidence interval, never a bare mean; say what the resampling unit is (seed, task instance, prompt);
  * compare methods with PAIRED differences when they share seeds/instances: it removes shared noise;
  * for aggregate scores over many tasks/runs prefer the interquartile mean (IQM) with a stratified bootstrap
    (Agarwal et al., "Deep RL at the Edge of the Statistical Precipice", NeurIPS 2021).
All functions take an explicit numpy Generator or seed so the reported interval is reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

DEFAULT_BOOT = 10_000


@dataclass(frozen=True)
class Interval:
    estimate: float
    low: float
    high: float
    n: int
    level: float = 0.95

    def __str__(self) -> str:
        return f"{self.estimate:.4g} [{self.low:.4g}, {self.high:.4g}] ({int(self.level * 100)}% CI, n={self.n})"

    def excludes(self, value: float = 0.0) -> bool:
        return not (self.low <= value <= self.high)


def _rng(rng) -> np.random.Generator:
    return rng if isinstance(rng, np.random.Generator) else np.random.default_rng(rng)


def _percentiles(boot: np.ndarray, level: float) -> tuple[float, float]:
    lo, hi = np.percentile(boot, [100 * (1 - level) / 2, 100 * (1 + level) / 2])
    return float(lo), float(hi)


def bootstrap_ci(values, statistic=np.mean, n_boot: int = DEFAULT_BOOT, level: float = 0.95, rng=0) -> Interval:
    """Percentile bootstrap CI of `statistic` over the first axis (the independent unit, e.g. seeds)."""
    x = np.asarray(values, dtype=float)
    if x.shape[0] < 2:
        raise ValueError("need at least 2 independent units for an interval")
    idx = _rng(rng).integers(0, x.shape[0], size=(n_boot, x.shape[0]))
    boot = np.array([statistic(x[i]) for i in idx])
    return Interval(float(statistic(x)), *_percentiles(boot, level), n=x.shape[0], level=level)


def paired_difference(a, b, n_boot: int = DEFAULT_BOOT, level: float = 0.95, rng=0) -> Interval:
    """CI of mean(a - b) where a[i] and b[i] share the unit i (same seed / instance / prompt)."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError(f"paired arrays must have the same shape, got {a.shape} and {b.shape}")
    return bootstrap_ci(a - b, n_boot=n_boot, level=level, rng=rng)


def iqm(values) -> float:
    """Interquartile mean: the mean of the middle 50% of all values (robust to outlier runs)."""
    x = np.sort(np.asarray(values, dtype=float).ravel())
    n = len(x)
    lo, hi = int(np.floor(0.25 * n)), int(np.ceil(0.75 * n))
    return float(x[lo:hi].mean())


def stratified_bootstrap(scores, statistic=iqm, n_boot: int = 2_000, level: float = 0.95, rng=0) -> Interval:
    """CI for an aggregate over a (runs, tasks) score matrix, resampling runs independently within each task."""
    s = np.asarray(scores, dtype=float)
    if s.ndim != 2:
        raise ValueError("scores must be (runs, tasks)")
    runs, tasks = s.shape
    g = _rng(rng)
    boot = np.empty(n_boot)
    for k in range(n_boot):
        idx = g.integers(0, runs, size=(runs, tasks))
        boot[k] = statistic(np.take_along_axis(s, idx, axis=0))
    return Interval(float(statistic(s)), *_percentiles(boot, level), n=runs, level=level)
