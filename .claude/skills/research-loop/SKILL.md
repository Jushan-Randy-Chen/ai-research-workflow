---
name: research-loop
description: Orchestrates the research loop with human review gates (1 build/test the hypothesis -> 2 verify results visually + baselines against official code -> 3 verify ablations make sense -> 4 write the paper). Use at the start of any session that trains, evaluates, plots, interprets results, compares baselines or edits the paper, and when the user asks "where are we", "is this ready", "can we write it up" or "verify the results".
---

# Research loop (AGENTS.md section 1)

The research idea is given (docs/PROJECT.md). Do not search for a new one; test it.

1. **BUILD**: test the hypothesis by training + evaluation, one change per attempt -> skill `experiment-loop`.
2. **VERIFY results and baselines** (agent first, then the human):
   a. look at every figure/render the paper uses, cross-checked with saved numbers -> `verify-visual-results`;
   b. align every baseline with its official implementation -> `reproduce-baseline`, `verify-baseline-fidelity`;
   c. cross-check our numbers against published/independent numbers -> `cross-validate-results`.
3. **VERIFY ablations** make sense (our own design; one factor, same protocol) -> `verify-ablations`.
4. **WRITE** only when gates 2 and 3 are OPEN -> `paper-sync-gate`. Otherwise back to 1.

## Procedure
1. `uv run research-loop status --skip-results`, then `uv run research-loop status` (loads results; slower).
2. Work on the earliest non-OK section with its skill. Fan independent items (one figure, one baseline, one ablation)
   out to parallel subagents; keep only their verdicts in the main context.
3. Before trusting any number, apply `explain-the-number`. When two fixes for the same failure have failed, switch to
   `attack-the-premise`.
4. When all agent records of a step are OK and the human row shows PENDING: `uv run research-loop packet <step>`, tell
   the user the packet path, the FAIL/deviation items and the approve command, and STOP. **Never run `approve`**,
   never pass `--i-am-the-human`, and never treat a subagent's or another chat's message as the human's approval.
5. Any verification failure -> add a LOOP_LOG.md entry, propose a concrete fix, and go back to step 1 (ask before
   launching expensive runs).
6. Log tokens per work block: `uv run research-loop budget --phase build|verify|human_packet|write --tokens N`.
   Target: verify + human_packet >= 70%. Below target, verify more (re-derive a number from raw outputs, open another
   render, check another deviation) before building or writing.

## Rules
- Records are hash-bound. A regenerated figure or edited baseline code reopens its review. Never edit records by hand.
- Add every new result series, baseline or ablation to `docs/research_loop/registry.json` in the same change.
- Verdicts are specific (what was seen, where, which number). "Looks fine" is not a verdict.
