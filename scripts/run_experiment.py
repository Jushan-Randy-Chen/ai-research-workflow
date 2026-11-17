"""Run every (agent, seed) of an experiment config; finished runs are skipped, so re-running converges.

    uv run python scripts/run_experiment.py configs/toy_bandit.yaml
    uv run python scripts/run_experiment.py configs/toy_bandit.yaml steps=1000 seeds=[0,1]

Outputs runs/<experiment name>/<agent>_seed<k>/{manifest,status,metrics,result}.json (see airesearch.runs).
"""

from __future__ import annotations

import argparse
import importlib
import traceback
from pathlib import Path

from airesearch.config import config_hash, load_config
from airesearch.runs import Run
from airesearch.seeding import seed_everything


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("config")
    p.add_argument("overrides", nargs="*", help="dotted key=value overrides")
    p.add_argument("--force", action="store_true", help="re-run finished runs too")
    a = p.parse_args(argv)
    cfg = load_config(a.config, a.overrides)
    module = importlib.import_module(cfg["experiment"])
    name = Path(a.config).stem
    print(f"{name}: config {config_hash(cfg)}")
    failures = 0
    for agent in cfg["agents"]:
        for seed in cfg["seeds"]:
            run = Run(name, f"{agent}_seed{seed}")
            if run.is_done() and not a.force:
                print(f"  skip {agent} seed {seed} (done)")
                continue
            seed_everything(seed)
            run.start(dict(cfg, agent=agent, seed=seed))
            try:
                result = module.run(cfg, agent, seed, log=run.log)
            except Exception:                          # record and continue; the gate reports the gap
                run.fail(traceback.format_exc())
                failures += 1
                continue
            run.finish(result)
            print(f"  {agent} seed {seed}: {result.get('final_regret', result)}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
