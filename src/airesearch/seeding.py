"""Seed every random number generator the experiment may touch, in one call."""

from __future__ import annotations

import os
import random

import numpy as np


def seed_everything(seed: int, deterministic: bool = False) -> np.random.Generator:
    """Seed python, numpy and (if installed) torch; return a numpy Generator to pass around explicitly.

    Prefer passing the returned Generator (or a torch.Generator) to the code that samples, instead of relying on
    global state. `deterministic=True` also asks torch/cuDNN for deterministic kernels (slower; use for debugging and
    for the final reproducibility check).
    """
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch
    except ImportError:
        return np.random.default_rng(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if deterministic:
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        torch.use_deterministic_algorithms(True)
        torch.backends.cudnn.benchmark = False
    return np.random.default_rng(seed)
