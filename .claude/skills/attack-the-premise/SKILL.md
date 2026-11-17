---
name: attack-the-premise
description: Use when two or more fixes for the same failure have failed, when results contradict the hypothesis, or when training/evaluation behaves unexpectedly and the cause is unknown. Finds the root cause and tests the shared assumption instead of trying another fix.
---

# Attack the premise, fix the root cause (adapted from poteto-mode; see docs/CREDITS.md)

1. **Reproduce** the failure with the smallest config and a fixed seed. Record the command.
2. **Write the premise**: the one sentence every failed fix assumed (e.g. "the reward signal is correct", "the
   baseline is converged", "the eval uses the trained checkpoint", "the model can represent the target").
3. **Test it directly** before any new fix: design an observation that would come out differently if the premise were
   false (log the reward on a hand-built trajectory; overfit a single batch; evaluate with the true goal/label as an
   oracle; render one episode; compare against the official implementation on the same input). Look at how failures
   are distributed (which tasks, seeds, steps), not only their average.
4. **Find the first wrong decision**: walk back from the symptom (data -> preprocessing -> model -> loss ->
   optimizer -> evaluation -> aggregation -> plotting) to the first place the state is wrong. Fix it there. Clamps,
   retries, skipping bad batches or seeds hide bugs; use them only if the state they handle is legitimate.
5. **Fix the pattern**: search for the same fault elsewhere (other tasks, other baselines, other scripts).
6. **Add the cheap signal** that would have shown this at first glance (an assert, a logged statistic, a unit test).
7. If the premise is the research hypothesis itself and the evidence contradicts it, say so plainly, record it in
   LOOP_LOG.md and DECISIONS.md, and propose: refine the hypothesis, narrow the claim, or stop.
