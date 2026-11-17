"""Provenance: everything needed to say which code, environment and config produced a result.

`collect()` is cheap and never raises; missing information is recorded as None instead.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import platform
import subprocess
import sys
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRACKED_PACKAGES = ("numpy", "torch", "jax", "gymnasium", "transformers")


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def git_state() -> dict:
    diff = _git("diff", "HEAD")
    return {
        "commit": _git("rev-parse", "HEAD"),
        "dirty": bool(diff) if diff is not None else None,
        # A dirty tree is allowed while exploring, but the diff hash pins exactly what ran.
        "diff_sha256": hashlib.sha256(diff.encode()).hexdigest() if diff else None,
    }


def package_versions(names=TRACKED_PACKAGES) -> dict:
    out = {}
    for name in names:
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            continue
    return out


def accelerator() -> dict:
    try:
        import torch
    except ImportError:
        return {"cuda": None}
    if not torch.cuda.is_available():
        return {"cuda": False}
    return {"cuda": True, "device": torch.cuda.get_device_name(0), "count": torch.cuda.device_count()}


def collect(config: dict | None = None) -> dict:
    lock = ROOT / "uv.lock"
    return {
        "time": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "command": " ".join(sys.argv),
        "git": git_state(),
        "uv_lock_sha256": sha256_file(lock) if lock.exists() else None,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "packages": package_versions(),
        "accelerator": accelerator(),
        "config": config,
    }
