---
name: verify-visual-results
description: Step 2a of the research loop. Verify every result by LOOKING at the figures, rollouts, renders or samples the paper relies on, cross-check what is seen against the saved numbers and the paper text, and record a hash-bound verdict per figure. Use after evaluations finish, after any figure is regenerated, before any paper push, or when research-loop shows visual items UNREVIEWED/STALE/FAIL.
---

# Verify results visually (step 2a)

A result counts as verified only after the agent has opened its image and checked it against the raw numbers.

1. `uv run research-loop figures` lists every figure the manuscript includes and its review state.
   `uv run research-loop status` also runs the registered result checks (existence, counts, value ranges).
2. For each UNREVIEWED/STALE figure (one subagent per figure group is fine):
   - Open it with the Read tool (PDF or the PNG twin written by `airesearch.figures.save`; confirm the twin's sha256
     matches the manifest if you use it).
   - Recompute two or three plotted values directly from the raw run outputs (result.json / arrays) and check the curve
     or bar shows them. Check every number the .tex states about this figure (grep the caption and text).
   - Every legend entry is visible and distinguishable; nothing hidden behind another series, an inset or an axis.
   - Axes, units, budgets, n and interval type match docs/PROTOCOL.md and the caption.
   - Qualitative evidence (rollout frames, generated samples, attention maps): the behaviour shown is what the text
     claims; success frames really show success; examples are not cherry-picked (state how they were selected).
   - Nothing contradicts the hypothesis silently (a baseline winning somewhere, a control condition behaving oddly).
     If it does, it is a finding, not a defect of the figure: report it.
3. Record: `uv run research-loop record-visual <name.pdf> --verdict pass|fail --summary "what was seen, with numbers"
   --findings '["..."]'`. For a regenerated file not yet copied into the paper add `--file <path>`; the record turns
   OK once identical bytes are in the paper.
4. Report FAILs to research-loop. Do not regenerate figures or edit the paper inside this skill.
