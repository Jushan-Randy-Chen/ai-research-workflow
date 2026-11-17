# Research practice: how to run this project without losing the thread

Opinionated guidance for hypothesis-driven ML/AI research aimed at top venues (NeurIPS, ICML, ICLR, CVPR, CoRL, ...).
The workflow in AGENTS.md enforces the mechanical parts; this file explains the judgment behind them.

## 1. Start from a falsifiable claim, not a method
- Write the one-sentence claim and its falsifier in PROJECT.md before writing code. If you cannot say what result would
  prove you wrong, you are not ready to run experiments.
- Prefer the smallest experiment that could falsify the claim (a toy, one task, one seed sweep) before scaling up.
  Most ideas die cheaply here, which is the point.
- Separate *mechanism* from *outcome*: "X improves success" is an outcome; "X improves success because it explores
  arms greedy abandons" is a mechanism, and it suggests the ablation and the diagnostic plot that test it.

## 2. The experiment loop: one change, one measurement, keep or revert
(Adapted from the Hillclimb playbook of poteto-mode; see CREDITS.md.)
- Freeze the evaluation harness before iterating: fixed split, metric, seeds, budget. Show it is sensitive (it
  separates a known-good from a known-bad configuration) and that it reports failures (crashed seeds, NaNs).
- Change one thing per attempt. Measure before and after with the frozen harness, over enough seeds to clear the
  noise. Keep only changes that beat the noise; revert everything else in full. Never stack untested changes.
- Log every attempt, kept or reverted, with the hypothesis that motivated it (`research-loop log-attempt`). The log is
  the memory of the project: it stops you retrying dead ideas and it writes half of the appendix.
- Ground each attempt in a mechanism ("the critic overestimates because ...; clip the target"), not "try a lower lr".
- Write the stop rule in advance (target AND minimum attempts). Do not relax it to declare victory.

## 3. Explain every number before you trust it
(Adapted from "Explain the Number" and the benchmark checklist of poteto-mode.)
- **Decide before you run**: what result would change your decision, and how large is seed-to-seed noise? If the
  spread is larger than the effect, the answer is "no measurable difference", not a trend.
- **Did it even happen?** Confirm the run used the checkpoint, data and config you think (provenance manifest), that
  every seed finished, and that failures are counted rather than silently dropped.
- **What else could it measure?** Train/test leakage, evaluation on training instances, a cached result, a metric bug,
  an untuned baseline, a different compute budget, a lucky seed. Rule each out with evidence.
- **Was the baseline tuned like ours?** An untuned baseline compares configurations, not methods.
- **Is it too good?** A result past what is plausible (perfect accuracy, a 1000x speedup) usually measured something
  else. Investigate before celebrating.
- **Does it matter?** Report effect sizes with CIs and the end-to-end metric a reader cares about.

## 4. Look at the artifacts, not only at the numbers
- Every figure, rollout video, generated sample or attention map that supports a claim is opened and looked at
  (step 2 of the loop). Many bugs are invisible in a mean and obvious in one rendered episode.
- Verify against the real artifact (the PDF the paper includes, the actual rollout), never a proxy ("the script exited
  0", "the file exists").

## 5. When fixes keep failing, attack the premise
(Adapted from "Attack the Premise" and "Fix Root Causes".)
- Two failed fixes that share an assumption mean the assumption is suspect. Write it down in one sentence and design
  an observation that would come out differently if it were false. Run that before the next fix.
- Debug to the first place the system did something wrong (data, labels, reward, preprocessing, eval) and fix it
  there; clamps, retries and "skip bad batches" usually hide the real bug.
- A negative result on a well-run experiment is information. Record it (LOOP_LOG.md) and decide: refine the
  hypothesis, narrow the claim, or stop.

## 6. Baselines and ablations
- Baselines: official code at a pinned commit, reproduce the authors' own number in their setting first, then adapt
  with the fewest possible changes, each listed and disclosed. Give them the same tuning budget you gave yourself.
- Ablations are your own experiments. Each removes or changes exactly one component, keeps everything else identical,
  and has a question whose answer is not known in advance. An ablation where both arms hit the ceiling answers nothing:
  make the setting harder or drop it.

## 7. Code that stays readable for the whole project
(Adapted from poteto-mode's Laziness Protocol, Minimize Reader Load, Make Operations Idempotent, Test Behavior.)
- Smallest change that solves the problem. One source of truth per decision (config value, constant, registry).
- Few layers: a reader should find "where does this number come from?" in under a minute. Inline one-caller wrappers.
- Every job is safe to re-run: atomic writes, explicit status, finished work skipped (`airesearch.runs`).
- Tests assert behaviour a user can observe (the metric is right on a hand-computed case, a resumed run equals an
  uninterrupted one), not internal call order.
- Encode lessons in structure: the second time you write the same warning, turn it into a test, an assert or a gate.

## 8. Writing
- Write the paper from CLAIMS.md: every sentence with a number points to a verified figure or table.
- Disclose every advantage your method has (extra information, compute, tuning) next to the result it affects.
- Figures: one message per figure, colour-blind-safe palette plus line styles, CIs shown, explanation in the caption.

## 9. Not losing track
- Session start: read AGENTS.md, `research-loop status`, the last LOOP_LOG entry and the tail of EXPERIMENT_LOG.tsv
  (skill `session-pickup`). The written trail is authoritative; do not redo finished work.
- Session end: commit work in progress, update the logs, write the next step in LOOP_LOG.md.
- Decisions go in DECISIONS.md with a date and a quote, the same day they are made.
