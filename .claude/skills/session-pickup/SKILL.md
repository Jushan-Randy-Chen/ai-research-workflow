---
name: session-pickup
description: Resume or pause research work without losing the thread. Use at the start of a session ("where were we", "continue", "pick up"), after a context reset, and when the user says to stop or pause for now.
---

# Session pickup and pause (adapted from poteto-mode's Session pickup / Pause safely; see docs/CREDITS.md)

## Pick up
1. Read AGENTS.md, then the trail, newest first: `uv run research-loop status --skip-results`, the last entry of
   docs/research_loop/LOOP_LOG.md, the tail of EXPERIMENT_LOG.tsv, DECISIONS.md (last 10 lines), `git log -10`,
   `git status`. Check running jobs (scheduler queue / `nvidia-smi` / status.json files under runs/).
2. The written trail is authoritative. Do not re-run finished experiments or re-derive recorded decisions. Name the
   resume point: the first unfinished item.
3. Verify inherited claims against the real artifacts only where a decision depends on them (a status file can be
   stale: check the process or the result file itself).
4. Route the remaining work to its skill (research-loop step) and continue.

## Pause
1. Stop at a safe boundary: finish or back out of the current atomic step; start nothing new.
2. Make work durable: commit code as a `wip:` commit (if the user allows commits), make sure running jobs write
   status files, and nothing lives only in the conversation.
3. Append to LOOP_LOG.md: what was being done, what is verified, what is running (paths), the next action.
4. Reply with where you are, what is on disk vs still running, and the first action on resume.
