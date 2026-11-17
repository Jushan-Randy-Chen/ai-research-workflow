# Claims -> evidence map

Every claim the paper makes, with the evidence that supports it. Nothing goes into the paper without a row here,
and a row is "verified" only when its figure/table has a passing visual review and its gate is open.

| # | Claim (as worded in the paper) | Evidence (figure / table / run paths) | Statistic (CI, n, unit) | Gate | Status |
|---|---|---|---|---|---|
| C1 | ... | paper/figures/x.pdf; runs/... | paired diff 4.1 [2.0, 6.3], n=5 seeds | 2 | draft / verified / dropped |

Rules
- Word claims at the strength of the evidence: "improves on all five tasks (95% CIs exclude zero)", not "significantly
  outperforms". If an interval includes zero, say "no measurable difference".
- A negative or null result that changes how a reader should use the method is a claim too. Report it.
- Dropped claims stay in the table (status "dropped", with the reason) so they do not creep back in.
