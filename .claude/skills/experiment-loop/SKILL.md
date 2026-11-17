---
name: experiment-loop
description: Step 1 of the research loop. Test the hypothesis by trial and error with a frozen evaluation harness: one change per attempt, measured over seeds, kept only if it beats the noise, every attempt logged. Use when training/evaluating to make a method work, tuning, debugging a training run, or "trying things".
---

# Experiment loop (adapted from poteto-mode's Hillclimb playbook; see docs/CREDITS.md)

You own the metric and the integrity of the experiment.

1. **Ground it.** Read docs/PROJECT.md (hypothesis, falsifier) and docs/PROTOCOL.md. Fix ONE metric, its direction,
   the evaluation split (never the test split for selection), and a stop rule written now: a target AND a minimum
   number of attempts (so one lucky run cannot end the loop). Use the user's numbers when given.
2. **Freeze the harness.** One command produces the metric over N seeds (e.g. `scripts/run_experiment.py` + a summary
   with `airesearch.stats`). Prove it is sensitive: a known-bad variant scores worse than the known-good one, and the
   seed spread is measured (run the reference twice). It must print failure counts (crashed seeds, NaN losses).
   Vet it with `explain-the-number`. Record the baseline value before any change.
3. **Loop, one hypothesis per attempt.** Each names a mechanism ("the value target is biased because ...; use a
   target network"), not "try something". Change ONE thing, run the frozen harness, compare with a paired CI.
   - Keep only if the improvement exceeds the noise and nothing else regressed. Otherwise revert in full.
   - Log it either way: `uv run research-loop log-attempt --hypothesis ... --change ... --command ... --seeds 0-4
     --metric ... --before ... --after ... --ci "[lo, hi]" --verdict kept|reverted|inconclusive --note ...`
   - One commit per kept change (only the files you changed).
   Independent hypotheses can run in parallel (separate run directories / worktrees), each still one change.
4. **Plateaus.** After several reverts in a row: re-read the code and data, look at rollouts/samples, combine
   near-misses, or try something more radical. If two fixes sharing one assumption failed, use `attack-the-premise`.
5. **Stop** when the stop rule is met or remaining ideas are not worth their cost. Never relax the rule to finish.
   Then hand over to verification (research-loop step 2).

Ask the user before launching runs that are expensive (GPU-days, paid APIs) or that touch shared machines.
Reply with: metric and target, baseline -> current (with CI), attempts kept vs reverted, the log path, next idea.
