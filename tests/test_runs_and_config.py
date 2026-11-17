import json

import pytest

from airesearch.config import apply_overrides, config_hash
from airesearch.runs import Run


def test_overrides_parse_values_and_reject_unknown_keys():
    cfg = {"train": {"lr": 0.1, "steps": 10}, "seeds": [0]}
    out = apply_overrides(cfg, ["train.lr=3e-4", "seeds=[0,1,2]"])
    assert out["train"]["lr"] == pytest.approx(3e-4) and out["seeds"] == [0, 1, 2] and cfg["train"]["lr"] == 0.1
    with pytest.raises(KeyError):
        apply_overrides(cfg, ["train.lrr=1"])


def test_config_hash_ignores_key_order():
    assert config_hash({"a": 1, "b": 2}) == config_hash({"b": 2, "a": 1})


def test_run_lifecycle_is_explicit_and_rerunnable(tmp_path):
    run = Run("exp", "r0", root=tmp_path)
    assert not run.is_done() and run.status["state"] == "absent"
    run.start({"lr": 1})
    run.log(step=0, loss=1.0)
    assert run.status["state"] == "running" and not run.is_done()
    manifest = json.loads((run.dir / "manifest.json").read_text())
    assert manifest["config"] == {"lr": 1} and "git" in manifest
    run.finish({"score": 0.5})
    assert run.is_done() and run.result() == {"score": 0.5}
    run.start({"lr": 1})                                    # restart: clean log, not done until finished again
    assert not run.is_done() and not (run.dir / "metrics.jsonl").exists()
    assert not list(run.dir.glob("*.tmp"))
