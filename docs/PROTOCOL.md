# Experimental protocol (fill in, then freeze before the main runs)

Write this BEFORE the runs whose numbers go into the paper, commit it, and change it only with a dated line in
DECISIONS.md. A protocol written after seeing results is a story, not a protocol.

## 1. Data and splits
- Train / validation / test (held-out) definitions, with how they are generated (seeds, instance indices, hashes).
- **The test split selects nothing**: no checkpoint, hyperparameter, early-stopping point, prompt or variant is chosen
  on it. Selection uses validation (or training instances) only; write down which.
- Leakage checks: near-duplicate / contamination search between train and test (for foundation models: check the
  pretraining corpus or cite why it cannot overlap).

## 2. Methods and baselines
- Every method's config file and the exact command. Baselines from official code (BASELINES.md).
- **Equal tuning budget**: same number of trials and the same selection rule for our method and each baseline.
- **Equal compute or equal samples**: state which budget is matched (environment steps, tokens, FLOPs, wall-clock,
  parameters) and report the other budgets too.

## 3. Metrics
- Primary metric (one), its exact definition, and the code that computes it. Secondary metrics.
- Write the decision rule before running: "we claim H1 if the paired difference's 95% CI excludes 0 on >= k of n tasks".

## 4. Seeds and statistics (`airesearch.stats`)
- Independent unit for resampling (seed, task instance, prompt) and the count (>= 5 seeds where affordable; say so
  when not).
- Report mean with 95% bootstrap CI; paired differences when methods share units; IQM + stratified bootstrap for
  aggregates over many tasks (Agarwal et al., NeurIPS 2021). No bare means, no "best seed".
- Noise floor: run the reference twice with different seeds before trusting any small difference.

## 5. Stopping and selection rules
- Which checkpoint is reported (final, or best-on-validation with the rule). Training length fixed in advance.
- Stop rule for the step-1 experiment loop (target AND a minimum number of attempts, so one lucky run cannot end it).

## 6. Reproducibility
- `uv.lock` committed; runs record git commit + diff hash, lockfile hash, hardware (`airesearch.provenance`).
- Determinism level (bitwise / statistical) and how it was checked: re-run one config end to end before submission.
- What will be released: code, configs, checkpoints, raw per-seed results, the scripts that make every figure/table.

## 7. Ablations
- Each ablation: the question, the ONE factor changed, the reference it is compared to, the hypotheses each outcome
  would support. Ablations are our own design and need not copy other papers; they must make sense (gates.SANITY).
