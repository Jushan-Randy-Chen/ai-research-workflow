---
name: explain-the-number
description: Checklist before trusting, reporting or acting on any measured number (a score, success rate, loss, speedup, scaling trend, benchmark result). Use whenever a result is about to be compared, plotted, claimed, or used to keep/revert a change.
---

# Explain the number (adapted from poteto-mode's Explain the Number + Benchmark checklist; see docs/CREDITS.md)

Write the claim you expect to make, in the words you would put in the paper. Then answer each question with
evidence from the run (files, logs, counts), not from reading the code.

1. **Decision before the run.** Which result would change the decision? What is the seed-to-seed spread? If the
   spread exceeds the effect, the verdict is "no measurable difference".
2. **Did it happen?** The manifest names the intended commit/config/checkpoint; every seed finished
   (status.json = done); the evaluation used the intended split and number of episodes/examples; outputs are correct,
   not just present (open a few).
3. **Did it error?** Count crashed seeds, NaNs, timeouts, invalid generations, clipped/filtered samples. Fast results
   often come from failures.
4. **What else could it measure?** Leakage or contamination; evaluating on training instances; cached or stale
   results; a metric/aggregation bug (mean of means, wrong denominator); different compute/sample budgets; a
   different preprocessing for one side; a lucky seed.
5. **Was each side tuned the same way?** Same tuning budget and selection rule for baselines and our method.
6. **Is it plausible?** Check limits: perfect scores, gains larger than the oracle/upper bound, results better than
   the official paper's own number for a baseline. Too good usually means measured something else.
7. **Does it reproduce?** >= 3-5 seeds, paired comparisons on shared units, 95% CI (`airesearch.stats`). Report n,
   the unit and the interval with the number.
8. **Does it matter?** Effect size on the metric readers care about; the end-to-end result, not only a sub-metric.

Verdict: holds / no measurable difference / inconclusive (name the unanswered question). Keep n, spread and the
evidence paths with the number wherever it is recorded (EXPERIMENT_LOG.tsv, CLAIMS.md).
