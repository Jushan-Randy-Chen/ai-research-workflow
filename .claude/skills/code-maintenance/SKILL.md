---
name: code-maintenance
description: Rules for writing and changing research code so it stays small, readable, re-runnable and tested - refactors, new experiment code, cleanup, adding tests, reviewing a diff. Use whenever editing code in src/, scripts/ or tests/.
---

# Code maintenance (adapted from poteto-mode's code principles; see docs/CREDITS.md)

- **Smallest change that solves it.** No new abstraction until a second real caller exists. Remove dead code first,
  then build on the simpler base. One source of truth per decision (config value, constant, registry entry).
- **Name the data shape first.** Before writing logic, write the types/array shapes that flow through it (e.g.
  `(seeds, tasks, episodes)`), and assert them at boundaries (data loading, results loading), not in every function.
- **Low reader load.** Few layers (inline one-caller wrappers), little mutable state (return values over mutation),
  plain dicts/dataclasses over class hierarchies. A reader finds where a number comes from in under a minute.
- **Re-runnable by construction.** Every job converges when re-run: atomic writes (`airesearch.runs.write_json_atomic`),
  explicit status files, finished work skipped, partial work detectable. Checkpoints written to a temp path and renamed.
- **Everything recorded.** Configs, not hard-coded constants; provenance manifest per run (`airesearch.provenance`).
- **Tests assert behaviour.** A test must fail if the behaviour breaks (wrong metric on a hand-computed example,
  resumed run != uninterrupted run, a baseline's loss differs from the official module on a fixed batch) and keep
  passing when only internals change. Derive expected values from the requirement, not from the code under test.
- **Small verifiable units.** Each change ends in a check (tests, a smoke run) before the next; one commit per unit.
- **Encode lessons in structure.** The second time a mistake happens, add a test, assert or gate rather than a note.
- **Don't move code running jobs depend on** without tracing who imports or launches it.
- Before finishing: `uv run ruff check .` and `uv run pytest` pass; summarise what changed and how it was verified.
