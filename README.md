# AI research workflow template

A starting point for hypothesis-driven ML/AI research aimed at top venues (NeurIPS, ICML, ICLR, CVPR, CoRL, ...).
It keeps a project straight from the first experiment to the camera-ready: what you are testing, what you tried,
what has been verified, and what may go into the paper. It is built to work with an AI coding agent (Claude Code
skills and hooks included) and with human review at the points where judgment matters.

```
           +---------------------------------------------------------------+
           v                                                               |
  1 BUILD: test the hypothesis      2 VERIFY: look at every result,    3 VERIFY: every ablation     4 WRITE: results go
  (frozen harness, one change   ->  baselines = official code,      -> makes sense (one factor, -> into the Overleaf
   per attempt, all logged)         numbers cross-checked              same protocol)              paper
                                    [agent, then HUMAN approves]       [agent, then HUMAN approves]
           ^                                 | fail                          | fail
           +---------------------------------+-------------------------------+
```

Gates are enforced, not just described: every verification is a record bound to the exact bytes it checked (figure,
baseline code, ablation question). Regenerate a figure and its review goes stale; the paper gate closes until it is
looked at again. Only a human can record the approval at steps 2 and 3.

## Quick start

```bash
git clone <this repo> my-project && cd my-project
uv sync                      # Python env from uv.lock (add --extra torch for PyTorch)
uv run pytest                # tests (seconds, CPU)
make example                 # worked example: Thompson sampling vs greedy bandits, 5 seeds, figure with CIs
uv run research-loop status  # the gate table
```

Then make it yours:
1. Fill in `docs/PROJECT.md` (one-sentence claim, hypotheses + falsifiers, scope) and `docs/PROTOCOL.md` (splits,
   metric, seeds, statistics, selection rules). Commit both before the main runs.
2. Add your experiment as `src/airesearch/experiments/<name>.py` with `run(config, agent, seed, log) -> dict`, and a
   config in `configs/`. (Rename the package if you like; keep `src/` layout.)
3. Register result series, baselines and ablations in `docs/research_loop/registry.json`.
4. Clone your Overleaf project into `paper/` (`scripts/overleaf.sh clone <project-id>`, see `paper/README.md`).
5. Delete the worked example (`toy_bandit.py`, its config, its registry entries) once your own experiment runs.

## What is inside

| Piece | Where | Why |
|---|---|---|
| Environment | `pyproject.toml`, `uv.lock`, `.python-version` | one locked environment, `uv run` everywhere |
| Library | `src/airesearch/` | small modules: config + overrides, seeding, re-runnable run dirs, provenance manifests, seed-aware statistics (bootstrap CIs, paired differences, IQM), publication figure style |
| Loop + gates | `src/airesearch/loop/`, CLI `research-loop` | gate table, hash-bound review records, human approval, review packets, experiment log, token budget |
| Agent guide | `AGENTS.md` (+ `CLAUDE.md` import) | the operating rules for humans and agents |
| Skills | `.claude/skills/` | `research-loop`, `session-pickup`, `experiment-loop`, `explain-the-number`, `attack-the-premise`, `verify-visual-results`, `reproduce-baseline`, `verify-baseline-fidelity`, `cross-validate-results`, `verify-ablations`, `literature-review`, `paper-sync-gate`, `research-paper-writing` (by Master-cai, MIT), `code-maintenance` |
| Hook | `.claude/settings.json` | prints the gate table at the start of every agent session |
| Project docs | `docs/` | PROJECT, PROTOCOL, CLAIMS (claim -> evidence), DECISIONS (dated), BASELINES, RESEARCH_PRACTICE (the judgment behind the rules) |
| References | `references/` | verified `refs.bib`, an index of papers and pinned reference code |
| Paper | `paper/` + `scripts/overleaf.sh` | Overleaf over plain git; pushes of changed figures/tables are refused while the paper gate is closed |
| CI | `.github/workflows/ci.yml` | `uv sync --locked`, ruff, pytest |

## Principles in one screen (details: docs/RESEARCH_PRACTICE.md)

- Start from a falsifiable claim; write what would prove you wrong before running anything.
- One change, one measurement, keep or revert; log every attempt with the mechanism it tested.
- Explain every number before trusting it: noise floor, did it run, what else could it measure, was the baseline tuned.
- Look at the artifacts (figures, rollouts, samples), not only the means.
- Baselines from official code, reproduced in their own setting first; deviations listed and disclosed.
- Ablations change one thing and must be able to tell the hypotheses apart.
- When two fixes fail for the same reason, test the premise.
- The test split selects nothing. Report CIs over seeds. Disclose every advantage.
- Write decisions down the same day; nothing important lives only in a chat.

## Credits

Parts of the experiment-loop and code-maintenance guidance are adapted from
[poteto-mode / pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan (MIT); see
`docs/CREDITS.md`. The `research-paper-writing` skill is by Master-cai (MIT, its LICENSE is included). MIT License.
