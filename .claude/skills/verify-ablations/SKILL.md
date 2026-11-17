---
name: verify-ablations
description: Step 3 of the research loop. Check that each ablation makes sense - it changes exactly one factor, uses the reference's checkpoints/data/seeds/budget, reproduces the reference, and its result answers its question. Ablations are our own design and need not copy other papers. Use when an ablation is added, changed or finished, or when research-loop shows ablations UNREVIEWED/STALE/FAIL.
---

# Verify ablations (step 3)

We design and run ablations ourselves; the check is that each one makes sense, not that it copies a published
protocol. Related work is optional context for the write-up.

One subagent per ablation in docs/research_loop/registry.json:
1. Restate the question and what each outcome would mean for the hypothesis.
2. Answer each sanity item (airesearch.loop.gates.SANITY) from evidence (config diffs, manifests, result files):
   `one_factor_changed`, `same_protocol`, `reference_reproduced`, `answers_question` (not at ceiling/floor for both
   arms; paired CI reported), `no_heldout_selection`.
3. Look at the ablation figure as in `verify-visual-results`; the curves must show what the finding says.
4. Verdict: `meaningful`, `weak` (runs fine but cannot separate the hypotheses; say what would make it informative),
   or `not_meaningful`. Note ablations a reviewer would expect that are missing.
5. Record: `uv run research-loop record-ablation <name> --verdict ... --sanity '{"one_factor_changed":true, ...}'
   --finding "one sentence with numbers" --summary "evidence and reasoning" [--related '["optional context"]']`.
