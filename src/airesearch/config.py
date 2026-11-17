"""Experiment configs: YAML file + dotted overrides, frozen once loaded, hashed for provenance.

    cfg = load_config("configs/toy_bandit.yaml", ["train.steps=2000", "seeds=[0,1,2]"])
    cfg["train"]["steps"]  # 2000

A config is a plain nested dict (easy to diff, dump and hash). Validate it at the boundary (in your experiment's
entry point) and pass plain values inward.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


def _parse_value(text: str) -> Any:
    value = yaml.safe_load(text)
    if isinstance(value, str):          # YAML 1.1 reads "3e-4" as a string; scientific notation is common in ML
        try:
            return float(text)
        except ValueError:
            return value
    return value


def apply_overrides(cfg: dict, overrides: list[str]) -> dict:
    """Return a copy of `cfg` with `a.b.c=value` overrides applied. Unknown keys are an error (catches typos)."""
    out = copy.deepcopy(cfg)
    for item in overrides:
        if "=" not in item:
            raise ValueError(f"override must look like key.path=value: {item!r}")
        key, value = item.split("=", 1)
        node = out
        parts = key.split(".")
        for part in parts[:-1]:
            if part not in node or not isinstance(node[part], dict):
                raise KeyError(f"unknown config section {part!r} in override {item!r}")
            node = node[part]
        if parts[-1] not in node:
            raise KeyError(f"unknown config key {key!r}; add it to the YAML first so every run records it")
        node[parts[-1]] = _parse_value(value)
    return out


def load_config(path: str | Path, overrides: list[str] | None = None) -> dict:
    cfg = yaml.safe_load(Path(path).read_text()) or {}
    return apply_overrides(cfg, overrides or [])


def config_hash(cfg: dict) -> str:
    """Stable short hash of a config (key order does not matter)."""
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, default=str).encode()).hexdigest()[:12]
