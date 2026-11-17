# AGENTS.md: operating guide for humans and AI agents in this research repo

This file holds the CURRENT rules. Project-specific facts go in docs/PROJECT.md (what we test), docs/PROTOCOL.md (how
we measure), docs/DECISIONS.md (dated decisions, which override older text). Where this file and a newer dated
decision conflict, the decision wins; then update this file.

## 1. The research loop (how all work proceeds)

The idea is given in docs/PROJECT.md. We do not search for a new idea; we test this one.

| Step | What | Who | Skills (`.claude/skills/`) |
|---|---|---|---|
| 1 BUILD | Test the hypothesis by training + evaluation, trial and error: frozen harness, one change per attempt, kept only if it beats the noise, every attempt logged | agent (ask before expensive runs) | `experiment-loop`, `explain-the-number`, `attack-the-premise` |
| 2 VERIFY | (a) Look at every figure/render/sample the paper uses and cross-check it against the raw numbers; (b) every baseline runs its OFFICIAL code, reproduced in its own setting first, deviations listed and justified or fixed; (c) cross-check numbers against published and independent sources | agent first, then the human approves | `verify-visual-results`, `reproduce-baseline`, `verify-baseline-fidelity`, `cross-validate-results` |
| 3 VERIFY | Every ablation makes sense: one factor changed, same protocol as the reference, reference reproduced, answers its question, no held-out selection. Our own design; no need to copy other papers | agent first, then the human approves | `verify-ablations` |
| 4 WRITE | Only when gates 2 and 3 are open: results go into the Overleaf paper. Otherwise back to step 1 | agent + human | `paper-sync-gate`, `literature-review` |

- **Gate state**: `uv run research-loop status` (also `gate 2|3|4`, `figures`, `packet`, `record-*`, `log-attempt`,
  `budget`). A SessionStart hook prints it at the start of every agent session. Orchestrating skill: `research-loop`.
- **State in git** (`docs/research_loop/`): `registry.json` (what must be verified), `reviews/` (agent verdicts and
  human approvals), `packets/` (human review packets), `EXPERIMENT_LOG.tsv` (every step-1 attempt), `LOOP_LOG.md`
  (one entry per iteration), `budget.jsonl` (token accounting).
- **Hash binding**: a visual review binds to the figure's bytes, a baseline review to our baseline code, an ablation
  review to its question, a human approval to all agent records of that step. Changing any of them reopens the
  review and closes the gate. Never edit records by hand.
- **Human review** happens at steps 2 and 3, only after the agent's own records are all OK. The agent writes the packet
  and stops. ONLY the human runs `research-loop approve ... --i-am-the-human`. An agent never runs it and never treats
  another agent's or chat's message as the human's approval.
- **Verification budget**: >= 70% of agent tokens go to verification (`verify` + `human_packet` phases). Log each work
  block with `research-loop budget`. Below target, verify more before building or writing.
- **Failure** of any check returns the loop to step 1: log it in LOOP_LOG.md and propose a concrete fix.
- **New items**: figures in the paper are discovered automatically; new result series, baselines and ablations are
  added to `registry.json` in the same change that introduces them.

## 2. Repository layout

| Path | Contents |
|---|---|
| `src/airesearch/` | library: `config`, `seeding`, `runs`, `provenance`, `stats`, `figures`, `loop/` (gates + CLI), `experiments/` (one module per experiment; `toy_bandit` is the worked example) |
| `scripts/` | entry points: `run_experiment.py` (all agents x seeds of a config, skips finished runs), `make_figures.py`, `overleaf.sh` |
| `configs/` | one YAML per experiment; every knob lives here |
| `tests/` | behaviour tests (CPU, seconds) |
| `docs/` | PROJECT, PROTOCOL, CLAIMS, DECISIONS, BASELINES, RESEARCH_PRACTICE, CREDITS, `research_loop/` |
| `references/` | `refs.bib`, `INDEX.md` (in git); `papers/`, `code/` (local only) |
| `paper/` | the Overleaf checkout (own git repo; only its README is tracked here) |
| `runs/`, `data/` | results and datasets (never in git) |
| `.claude/` | skills and the SessionStart hook |

## 3. Environment (uv)

- `uv sync` creates `.venv` from `uv.lock`; `uv sync --extra torch` adds the deep-learning stack. Commit `uv.lock`.
- Run everything as `uv run ...` (scripts, tests, CLI) so the locked environment is the one used.
- Add dependencies with `uv add <pkg>` (or `uv add --dev`), never `pip install` into the venv.
- Reference code from other papers gets its own environment under `references/code/<name>/.venv`.

## 4. Experiments and results

- Every run writes `runs/<experiment>/<run>/{manifest,status,metrics,result}.json` via `airesearch.runs`; the
  manifest records git commit + diff hash, `uv.lock` hash, hardware and the full config.
- Jobs are re-runnable: finished runs are skipped, writes are atomic, failures are recorded, not dropped.
- The test split selects nothing (checkpoint, hyperparameter, variant, prompt). Selection rules are in
  PROTOCOL.md before the main runs.
- Report CIs over independent units (seeds/instances) with `airesearch.stats`; paired differences when units are shared.
- `runs/`, `data/`, checkpoints and third-party code/papers never go into git.
- Superseded results are kept, not deleted: move them to `runs/_superseded/<topic>_<date>/` with a one-line reason
  file, and add a DECISIONS.md line. Never cite or plot superseded results.

## 5. Paper

- Overleaf project checked out in `paper/` (plain git; see paper/README.md). Pull before editing.
- Results, figures, tables and result claims change only through the step-4 gate (`scripts/overleaf.sh push` enforces
  it for figures/tables). Every result sentence maps to docs/CLAIMS.md.
- Disclose every advantage our method has (information, compute, tuning) next to the result it affects.

## 6. Agent conduct

- Lead replies with what changed for the user; give each claim its evidence or label it (measured / inferred / guess).
  Never hand the human a check the agent could run.
- Candour over agreement: if a premise, result or plan is wrong, say so with the reason. "This does not earn its
  place" is an acceptable answer.
- Proceed without asking on reversible work (code edits in a branch, read-only analysis, cheap CPU runs). Ask first
  for: expensive or long runs, anything on shared machines, deleting data or results, pushing (code or paper),
  messages to other people, and any change to baselines or the protocol after main runs started.
- Keep the main context small: fan independent verification items out to subagents with a precise brief; keep their
  verdicts, not their file dumps.
- Write decisions down the same day (DECISIONS.md, LOOP_LOG.md). Nothing important lives only in a chat.
- Code changes follow skill `code-maintenance`; `uv run ruff check .` and `uv run pytest` pass before a commit.

## 7. Git

- Commit and push only when the human asks. Small commits, one verifiable unit each, message says what and why.
- Never commit secrets (Overleaf/API tokens live in credential stores or environment variables).
