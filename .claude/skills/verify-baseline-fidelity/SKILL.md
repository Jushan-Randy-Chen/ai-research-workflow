---
name: verify-baseline-fidelity
description: Step 2b of the research loop. Check that each baseline matches its official implementation without manual changes - diff our code/config against the pinned official repository, list every deviation, and record a hash-bound verdict. Use when a baseline's code or config changes, when research-loop shows a baseline UNREVIEWED/STALE/FAIL, or when the user asks whether a baseline is faithful.
---

# Verify baseline fidelity (step 2b)

Standard: the baseline runs the official code and recipe. Every difference is a deviation that is either justified
(required for a fair comparison AND disclosed in the paper), fixed, or open.

One subagent per baseline:
1. Read its entry in docs/research_loop/registry.json and docs/BASELINES.md. Confirm the official repository from the
   paper itself and pin a commit (see `reproduce-baseline` step 2).
2. Compare item by item, citing file:line on both sides: architecture and parameter count; loss and targets; data,
   labels and preprocessing; optimizer, learning rate, schedule, batch size, number of updates; context length /
   sequence length; exploration and evaluation rules (sampling vs greedy, temperature, number of samples); observation
   and action processing; seeds, instances and budgets; the success metric and its aggregation.
3. Where possible, test equivalence without training: same input -> same forward output / loss as the official module;
   same evaluation of a fixed checkpoint. Note what could not be checked.
4. Classify each deviation {what, official, ours, status: justified|fixed|open, why}. Grep the paper to confirm each
   justified deviation is disclosed.
5. Record: `uv run research-loop record-baseline <name> --verdict aligned|deviates --official-commit <sha>
   --deviations '<json>' --summary "..."` (`aligned` is refused while any deviation is open).
6. Never change a baseline to improve its numbers or ours without the user's approval; report instead.
