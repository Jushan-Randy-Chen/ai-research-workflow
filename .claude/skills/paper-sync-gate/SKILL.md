---
name: paper-sync-gate
description: Step 4 of the research loop. Sync the Overleaf manuscript (git) and gate any change that puts results, figures, tables or result claims into it. Use before editing the paper, before any Overleaf push, and when the user asks to sync with Overleaf.
---

# Paper sync gate (step 4)

1. **Sync** (always allowed): `scripts/overleaf.sh pull`. On conflicts, stop and show the user.
2. **Gate**: `uv run research-loop gate 4`.
   - CLOSED: do not add or change results, figures, tables or result claims; tell the user which sections are not OK.
     Wording, related work, typos and layout edits that touch no result are allowed.
   - OPEN: proceed.
3. **Every number traceable**: each result sentence maps to a row in docs/CLAIMS.md with a verified figure/table.
   Phrase claims at the strength of the evidence (CIs, n, unit); disclose every advantage our method has next to the
   result it affects.
4. **Figures/tables** come only from scripts. Regenerate -> review with `record-visual <name> --file <file>` -> copy
   into paper/figures or paper/tables -> `scripts/overleaf.sh push "message"` (refused while gate 4 is closed and
   figures/tables changed). Commit/push only when the user asks.
5. Respect the author's voice: if the user writes the prose, give facts, numbers and suggestions rather than large
   blocks of text.

## Writing quality
For drafting or revising any section (abstract, introduction, related work, method, experiments, conclusion),
figure/table presentation, claim-evidence alignment and the pre-submission self-review, use skill
`research-paper-writing` (its `references/paper-review.md` is the adversarial review). Results still pass this gate
first.
