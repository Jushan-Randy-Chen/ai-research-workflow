"""Verification gates of the research loop.

  1 BUILD    test the hypothesis by training + evaluation; one change per attempt, logged in EXPERIMENT_LOG.tsv
  2 VERIFY   (a) every result is checked by LOOKING at its figures/renders, cross-checked with the saved numbers;
             (b) every baseline matches its official implementation; each deviation listed and justified or fixed.
             The agent verifies first, then a human approves (gate 2).
  3 VERIFY   every ablation makes sense (one factor changed, same protocol, reference reproduced, answers its
             question, no held-out selection). The agent verifies first, then a human approves (gate 3).
  4 WRITE    only when gates 2 and 3 are open: results go into the paper. Otherwise back to 1.

State lives in git under docs/research_loop/ (registry.json, reviews/, packets/, budget.jsonl, LOOP_LOG.md,
EXPERIMENT_LOG.tsv). Every review is bound to content hashes: regenerating a figure, editing baseline code or changing
an ablation question makes the review STALE and closes the gate again. Only a human records an approval.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import importlib
import json
import os
import re
from pathlib import Path

from airesearch.provenance import ROOT as _PACKAGE_ROOT
from airesearch.provenance import sha256_file

PHASES = ("build", "verify", "human_packet", "write")
VERIFY_PHASES = ("verify", "human_packet")
VERIFY_SHARE_TARGET = 0.70
SECTIONS_FOR_GATE = {
    2: ("results", "visual", "baselines", "human2"),
    3: ("ablations", "human3"),
    4: ("results", "visual", "baselines", "human2", "ablations", "human3"),
}
SANITY = {
    "one_factor_changed": "differs from the reference in exactly the factor named by the question",
    "same_protocol": "same checkpoints/data/seeds/budget/metric as the reference (or the difference IS the factor)",
    "reference_reproduced": "the reference numbers inside the ablation run match the main result",
    "answers_question": "the result can separate the hypotheses (not at ceiling/floor for both arms; CI reported)",
    "no_heldout_selection": "no held-out/test score selected any checkpoint, hyperparameter or variant",
}
LOG_COLUMNS = ("id", "date", "hypothesis", "change", "command", "seeds", "metric", "before", "after", "ci",
               "verdict", "note")
VERDICTS = ("kept", "reverted", "inconclusive")


def find_root(start: Path | None = None) -> Path:
    """Project root: $RESEARCH_ROOT, else the nearest parent of cwd with docs/research_loop, else the package's."""
    if os.environ.get("RESEARCH_ROOT"):
        return Path(os.environ["RESEARCH_ROOT"]).resolve()
    here = (start or Path.cwd()).resolve()
    for d in (here, *here.parents):
        if (d / "docs/research_loop/registry.json").exists():
            return d
    return _PACKAGE_ROOT


def now() -> str:
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text)).strip("_")


class Loop:
    """All paths of one project's loop state. Every check is a method returning rows (item, state, note)."""

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root).resolve() if root else find_root()
        self.dir = self.root / "docs/research_loop"
        self.reviews = self.dir / "reviews"
        self.budget_path = self.dir / "budget.jsonl"
        self.log_path = self.dir / "EXPERIMENT_LOG.tsv"

    # ------------------------------------------------------------------ registry and records
    def registry(self) -> dict:
        return json.loads((self.dir / "registry.json").read_text())

    def path(self, p: str) -> Path:
        q = Path(p)
        return q if q.is_absolute() else self.root / q

    def record_path(self, kind: str, key: str) -> Path:
        return self.reviews / kind / f"{slug(key)}.json"

    def load_record(self, kind: str, key: str) -> dict | None:
        p = self.record_path(kind, key)
        return json.loads(p.read_text()) if p.exists() else None

    def write_record(self, kind: str, key: str, record: dict) -> Path:
        p = self.record_path(kind, key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(dict(record, recorded=now()), indent=1, sort_keys=True) + "\n")
        return p

    # ------------------------------------------------------------------ paper figures
    def paper_figures(self) -> list[Path]:
        """Every figure the manuscript includes (uncommented \\includegraphics), sorted and unique."""
        draft = self.path(self.registry().get("manuscript", "paper"))
        found = set()
        for tex in draft.rglob("*.tex") if draft.exists() else []:
            for line in tex.read_text(errors="replace").splitlines():
                line = re.sub(r"(?<!\\)%.*", "", line)
                for name in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", line):
                    p = draft / name
                    if not p.suffix:
                        p = next((p.with_suffix(e) for e in (".pdf", ".png", ".jpg") if p.with_suffix(e).exists()), p)
                    found.add(p)
        return sorted(found)

    # ------------------------------------------------------------------ checks
    def check_results(self) -> list[tuple]:
        reg = self.registry()
        rows = []
        for item in reg.get("results", []):
            hits = sorted(self.root.glob(item["glob"]))
            need = item.get("min_count", 1)
            state = "OK" if len(hits) >= need else "MISSING"
            rows.append((item["name"], state, f"{len(hits)}/{need} files match {item['glob']}"))
        for ref in reg.get("result_checks", []):          # project-specific checks: "module:function" -> rows
            module, fn = ref.split(":")
            rows.extend(getattr(importlib.import_module(module), fn)(self))
        return rows

    def check_visual(self) -> list[tuple]:
        rows = []
        for fig in self.paper_figures():
            rec = self.load_record("visual", fig.name)
            if not fig.exists():
                rows.append((fig.name, "MISSING", f"figure file not found: {fig}"))
            elif rec is None:
                rows.append((fig.name, "UNREVIEWED", "no visual review"))
            elif rec.get("sha256") != sha256_file(fig):
                rows.append((fig.name, "STALE", f"figure changed since review {rec.get('recorded')}"))
            elif rec.get("verdict") != "pass":
                rows.append((fig.name, "FAIL", rec.get("summary", "")))
            else:
                rows.append((fig.name, "OK", rec.get("summary", "")))
        return rows

    def baseline_files(self, entry: dict) -> dict:
        return {p: sha256_file(self.path(p)) for p in entry["our_code"] if self.path(p).exists()}

    def check_baselines(self) -> list[tuple]:
        rows = []
        for name, entry in self.registry().get("baselines", {}).items():
            rec = self.load_record("baseline", name)
            missing = [p for p in entry["our_code"] if not self.path(p).exists()]
            if missing:
                rows.append((name, "MISSING", "code not found: " + ", ".join(missing)))
            elif rec is None:
                rows.append((name, "UNREVIEWED", f"no fidelity review against {entry['official']['repo']}"))
            elif rec.get("files") != self.baseline_files(entry):
                rows.append((name, "STALE", f"our code changed since review {rec.get('recorded')}"))
            elif rec.get("verdict") != "aligned":
                n_open = sum(d.get("status") == "open" for d in rec.get("deviations", []))
                rows.append((name, "FAIL", f"{rec.get('verdict')}; {n_open} open deviation(s)"))
            else:
                rows.append((name, "OK", f"{len(rec.get('deviations', []))} justified deviation(s) disclosed"))
        return rows

    def check_ablations(self) -> list[tuple]:
        rows = []
        for name, entry in self.registry().get("ablations", {}).items():
            rec = self.load_record("ablation", name)
            if rec is None:
                rows.append((name, "UNREVIEWED", entry["question"]))
                continue
            failed = [k for k in SANITY if not rec.get("sanity", {}).get(k)]
            if rec.get("question") != entry["question"]:
                rows.append((name, "STALE", "ablation question changed since review"))
            elif failed:
                rows.append((name, "FAIL", "sanity not met: " + ", ".join(failed)))
            elif rec.get("verdict") != "meaningful":
                rows.append((name, "FAIL", rec.get("summary", "")))
            else:
                rows.append((name, "OK", rec.get("finding", "")))
        return rows

    def step_records(self, step: int) -> dict:
        kinds = ("visual", "baseline") if step == 2 else ("ablation",)
        return {f"{k}/{p.name}": sha256_file(p) for k in kinds for p in sorted((self.reviews / k).glob("*.json"))}

    def check_human(self, step: int, agent_ok: bool) -> tuple:
        key = f"human step {step}"
        p = self.reviews / "human" / f"step{step}.json"
        if not agent_ok:
            return (key, "BLOCKED", f"agent verification of step {step} is not complete")
        if not p.exists():
            return (key, "PENDING", f"awaiting human review: research-loop packet {step}")
        rec = json.loads(p.read_text())
        if rec.get("bound_digest") != digest(self.step_records(step)):
            return (key, "STALE", f"agent records changed since approval {rec.get('approved')}")
        if rec.get("decision") != "approve":
            return (key, "FAIL", f"human decision {rec.get('decision')}: {rec.get('notes', '')}")
        return (key, "OK", f"approved by {rec.get('approver')} at {rec.get('approved')}")

    def report(self, results: bool = True) -> dict:
        out = {}
        if results:
            out["results"] = self.check_results()
        out["visual"] = self.check_visual()
        out["baselines"] = self.check_baselines()
        out["human2"] = [self.check_human(2, all(section_ok(k, out[k]) for k in ("visual", "baselines", "results")
                                                 if k in out))]
        out["ablations"] = self.check_ablations()
        out["human3"] = [self.check_human(3, all_ok(out["ablations"]))]
        return out

    # ------------------------------------------------------------------ budget and experiment log
    def budget(self) -> tuple[dict, float | None]:
        totals = dict.fromkeys(PHASES, 0)
        if self.budget_path.exists():
            for line in self.budget_path.read_text().splitlines():
                if line.strip():
                    row = json.loads(line)
                    totals[row["phase"]] = totals.get(row["phase"], 0) + int(row["tokens"])
        total = sum(totals.values())
        return totals, (sum(totals[p] for p in VERIFY_PHASES) / total if total else None)

    def add_budget(self, phase: str, tokens: int, note: str = "") -> None:
        if phase not in PHASES:
            raise ValueError(f"phase must be one of {PHASES}")
        with open(self.budget_path, "a") as f:
            f.write(json.dumps({"time": now(), "phase": phase, "tokens": int(tokens), "note": note}) + "\n")

    def log_attempt(self, **row) -> int:
        """Append one attempt to EXPERIMENT_LOG.tsv (hillclimb-style decision log); returns its id."""
        if row.get("verdict") not in VERDICTS:
            raise ValueError(f"verdict must be one of {VERDICTS}")
        if not self.log_path.exists():
            self.log_path.write_text("\t".join(LOG_COLUMNS) + "\n")
        n = sum(1 for _ in self.log_path.open()) - 1
        row = dict(row, id=n + 1, date=now()[:10])
        clean = [str(row.get(c, "")).replace("\t", " ").replace("\n", " ") for c in LOG_COLUMNS]
        with open(self.log_path, "a") as f:
            f.write("\t".join(clean) + "\n")
        return n + 1


# A section with no items is vacuously fine, except these: no results or no paper figures means nothing was verified.
MUST_BE_NONEMPTY = ("results", "visual")


def all_ok(rows) -> bool:
    return all(r[1] == "OK" for r in rows)


def section_ok(name: str, rows) -> bool:
    return all_ok(rows) and (bool(rows) or name not in MUST_BE_NONEMPTY)


def gate_open(report: dict, step: int) -> bool:
    return all(section_ok(k, report[k]) for k in SECTIONS_FOR_GATE[step] if k in report)
