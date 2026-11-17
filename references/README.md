# references/: literature and reference code

| Path | What | In git? |
|---|---|---|
| `INDEX.md` | one row per paper/codebase we rely on: why it matters, what we take from it, verification status | yes |
| `refs.bib` | master bibliography (entries verified against the publisher page; see skill `literature-review`) | yes |
| `papers/` | PDFs for local reading | no (copyright) |
| `code/<name>/` | read-only clones of official baseline repositories at a pinned commit | no (licenses vary) |

Rules
- Never cite from memory: every bib entry is checked against OpenReview / PMLR / NeurIPS proceedings / CVF / ACL
  Anthology / arXiv (title, authors, venue, year). Prefer the published version over arXiv when it exists.
- Clone reference code read-only into an empty directory and record the commit in INDEX.md and BASELINES.md. Do not
  run third-party code from inside the clone with your repo's interpreter on PYTHONPATH; build its own environment
  (`uv venv references/code/<name>/.venv`) when you need to execute it.
