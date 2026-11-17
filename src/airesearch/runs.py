"""Run directories that are safe to re-run: atomic writes, explicit status, a done marker.

Layout:   runs/<experiment>/<run_name>/
            manifest.json   provenance + config (written when the run starts)
            status.json     {"state": "running" | "done" | "failed", ...}
            metrics.jsonl   one JSON object per logged step
            result.json     final metrics (written last; its presence + state "done" means complete)

Re-running the same command converges: a finished run is skipped, an unfinished one is restarted (or resumed by the
caller from its own checkpoints). Nothing is ever half-written, because every JSON goes through a temp file + rename.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from airesearch import provenance

RUNS = provenance.ROOT / "runs"


def write_json_atomic(path: str | Path, obj) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=str)
        f.write("\n")
    os.replace(tmp, path)
    return path


class Run:
    def __init__(self, experiment: str, name: str, root: str | Path | None = None):
        self.dir = Path(root or RUNS) / experiment / name

    @property
    def status(self) -> dict:
        path = self.dir / "status.json"
        return json.loads(path.read_text()) if path.exists() else {"state": "absent"}

    def is_done(self) -> bool:
        return self.status.get("state") == "done" and (self.dir / "result.json").exists()

    def start(self, config: dict) -> Run:
        self.dir.mkdir(parents=True, exist_ok=True)
        write_json_atomic(self.dir / "manifest.json", provenance.collect(config))
        write_json_atomic(self.dir / "status.json", {"state": "running"})
        (self.dir / "metrics.jsonl").unlink(missing_ok=True)   # restart from a clean log
        return self

    def log(self, **metrics) -> None:
        with open(self.dir / "metrics.jsonl", "a") as f:
            f.write(json.dumps(metrics, default=float) + "\n")

    def finish(self, result: dict) -> None:
        write_json_atomic(self.dir / "result.json", result)
        write_json_atomic(self.dir / "status.json", {"state": "done"})

    def fail(self, error: str) -> None:
        write_json_atomic(self.dir / "status.json", {"state": "failed", "error": error})

    def result(self) -> dict:
        return json.loads((self.dir / "result.json").read_text())
