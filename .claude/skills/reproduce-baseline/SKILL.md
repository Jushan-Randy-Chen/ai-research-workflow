---
name: reproduce-baseline
description: Bring in a baseline from another paper by reproducing it from its OFFICIAL code before adapting it - find and pin the official repository, reproduce a number the authors reported in their own setting, then port to our setting with minimal, documented changes. Use when adding a baseline, when a baseline underperforms suspiciously, or when the user asks to "reproduce X".
---

# Reproduce a baseline

1. **Identify the source of truth.** From the paper itself (PDF footnote, abstract page, project page, OpenReview)
   find the official repository; distrust forks and blog re-implementations. If no official code exists, say so and
   pick the most-cited implementation endorsed by the authors or by a later paper that reproduced the numbers.
2. **Pin it.** Clone read-only into a new empty directory `references/code/<name>` (git-ignored), record the commit
   in references/INDEX.md and docs/BASELINES.md. Read its README, configs and the paper's hyperparameter table;
   note mismatches between paper and code (code usually wins; record both).
3. **Reproduce in their setting first.** Build its own environment (`uv venv references/code/<name>/.venv`, install
   its pinned requirements; do not import it into our environment). Run the smallest reported configuration and
   compare with the reported number (same metric definition, seeds, budget). Verdict: reproduced / within noise /
   not reproduced. Not reproduced -> investigate (environment versions, seeds, evaluation protocol) before going on.
   Ask the user before runs that need significant compute.
4. **Port to our setting with minimal changes.** Prefer wrapping their code (adapter for our env/data interface)
   over rewriting it. Each necessary change (env interface, horizon, observation format, split, budget) goes into
   docs/BASELINES.md as a deviation with its reason. Give the baseline the same tuning budget as our method, selected
   on validation only.
5. **Hand over** to `verify-baseline-fidelity` (records the deviations, hash-bound) and add the baseline to
   docs/research_loop/registry.json.
