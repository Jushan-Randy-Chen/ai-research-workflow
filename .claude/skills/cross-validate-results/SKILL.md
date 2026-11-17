---
name: cross-validate-results
description: Cross-check our numbers against independent sources - published numbers for the same baseline/setting, an independent re-computation of the metric from raw outputs, a second evaluation pipeline, or re-runs with fresh seeds. Use before results go into the paper, when our baseline numbers differ from published ones, or when a result looks surprisingly good or bad.
---

# Cross-validate results

1. **Against the literature.** For each baseline/benchmark pair, find published numbers in a comparable setting
   (`literature-review` for sources; open the paper's table, cite table/figure number). Build a table: published
   value, setting differences, our value with CI. Large unexplained gaps (ours much lower for a baseline, or much
   higher for our method than any related result) must be investigated with `explain-the-number` before use.
2. **Independent metric computation.** Recompute the headline metric from the raw per-episode/per-example outputs with
   a short script written independently of the evaluation code (different aggregation path), and compare exactly.
3. **Independent evaluation.** Where the benchmark has an official evaluator or leaderboard script, evaluate one saved
   checkpoint with it and compare with our evaluator.
4. **Fresh seeds.** Re-run the main comparison (or its cheapest faithful slice) with seeds never used during
   development; the conclusion must hold. Ask before expensive runs.
5. Record the outcome in docs/CLAIMS.md (evidence column) and, if a gap remains, in LOOP_LOG.md as an open item.
