# Project brief (fill this in first; keep it to one page)

The single source of truth for WHAT we are testing. Everything else (configs, runs, figures, paper) traces back here.
When it changes, add a dated line to DECISIONS.md saying why.

## One-sentence claim
> On <setting>, <method> achieves <measurable outcome> compared with <baselines>, because <mechanism>.

(Example, the worked toy: "On Bernoulli bandits, Thompson sampling has lower cumulative regret than greedy-on-the-
posterior-mean, because greedy can lock onto a sub-optimal arm.")

## Hypotheses and what would falsify them
| ID | Hypothesis (mechanism) | Prediction we will measure | Result that would falsify it |
|---|---|---|---|
| H1 | ... | metric, setting, direction | ... |

## Scope
- **In**: tasks/datasets, splits, model sizes, compute budget per run, venue + deadline.
- **Out (non-goals)**: what we will NOT do this paper (write it down; it stops scope creep).
- **Deferred**: ideas parked for later, with the date they were parked.

## Methods
| Name in code | Name in paper | Role (method / baseline / ablation) | Config | Official code (baselines) |
|---|---|---|---|---|

## Evaluation protocol
See PROTOCOL.md. Main metric, held-out split, seeds, budget, statistics.

## Status
Current loop iteration and gate state: `uv run research-loop status`. Iteration history: research_loop/LOOP_LOG.md.
