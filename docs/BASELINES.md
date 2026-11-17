# Baselines

One section per baseline. A baseline is only as credible as its alignment with the official implementation.
Workflow: skills `reproduce-baseline` (reproduce the paper's own number in the paper's own setting first) and
`verify-baseline-fidelity` (diff against the pinned official code; every deviation listed).

## <Baseline name>
- **Paper**: authors, title, venue, year, link.
- **Official code**: URL @ commit `<sha>` (cloned read-only to `references/code/<name>`; not committed).
- **Reproduction in the paper's setting**: our number vs the paper's reported number (table/figure reference),
  seeds, CI. Verdict: reproduced / within noise / not reproduced (with the investigation).
- **Adaptation to our setting**: what had to change (env interface, horizon, data split) and nothing else.
- **Deviations** (also recorded by `research-loop record-baseline`):
  | What | Official | Ours | Status (justified / fixed / open) | Why | Disclosed in paper? |
  |---|---|---|---|---|---|
- **Tuning budget**: the same number of configurations/seeds as our method got, selected on validation only.
