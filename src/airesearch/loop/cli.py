"""`research-loop`: the gates of the research loop (see airesearch/loop/gates.py and AGENTS.md section 1).

  status [--verbose] [--skip-results]   gate table + token share; exit 0 iff gate 4 (write) is open
  gate {2,3,4}                          exit 0 iff that gate is open
  figures                               the paper's included figures and their review state
  record-visual FIG [--file CANDIDATE] --verdict pass|fail --summary TEXT [--findings JSON]      (agent)
  record-baseline NAME --verdict aligned|deviates --official-commit SHA --deviations JSON --summary TEXT  (agent)
  record-ablation NAME --verdict meaningful|weak|not_meaningful --sanity JSON --finding TEXT --summary TEXT (agent)
  packet {2,3}                          write the human review packet under docs/research_loop/packets/
  approve {2,3} --approver NAME --decision approve|reject --i-am-the-human                        (HUMAN ONLY)
  log-attempt --hypothesis ... --change ... --verdict kept|reverted|inconclusive [...]          (step 1 log)
  budget --phase build|verify|human_packet|write --tokens N                                     (token share)
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys
from pathlib import Path

from airesearch.loop import gates as G
from airesearch.provenance import sha256_file


def _table(rows) -> str:
    width = max([len(r[0]) for r in rows] + [4])
    return "\n".join(f"  {r[0]:<{width}}  {r[1]:<10} {r[2]}" for r in rows)


def cmd_status(loop: G.Loop, a) -> int:
    rep = loop.report(results=not a.skip_results)
    for section, rows in rep.items():
        ok = sum(r[1] == "OK" for r in rows)
        if not rows and section in G.MUST_BE_NONEMPTY:
            print(f"[{section}] no items yet: gate stays closed until there is at least one")
            continue
        print(f"[{section}] {ok}/{len(rows)} OK")
        shown = rows if a.verbose else [r for r in rows if r[1] != "OK"]
        if shown:
            print(_table(shown))
    for step in (2, 3, 4):
        print(f"gate {step}: {'OPEN' if G.gate_open(rep, step) else 'CLOSED'}")
    totals, share = loop.budget()
    print(f"tokens: {totals}; verification share "
          f"{'n/a' if share is None else f'{100 * share:.0f}%'} (target >= {100 * G.VERIFY_SHARE_TARGET:.0f}%)")
    return 0 if G.gate_open(rep, 4) else 1


def cmd_gate(loop, a) -> int:
    is_open = G.gate_open(loop.report(results=not a.skip_results), a.step)
    print(f"gate {a.step} {'OPEN' if is_open else 'CLOSED'}")
    return 0 if is_open else 1


def cmd_figures(loop, a) -> int:
    for fig, row in zip(loop.paper_figures(), loop.check_visual(), strict=True):
        print(f"{row[1]}\t{fig}\t{sha256_file(fig)[:12] if fig.exists() else '-'}")
    return 0


def _figure(loop, name) -> Path:
    for fig in loop.paper_figures():
        if name in (fig.name, str(fig)):
            return fig
    raise SystemExit(f"{name} is not an included figure of the manuscript")


def cmd_record_visual(loop, a) -> int:
    fig = _figure(loop, a.figure)
    looked = Path(a.file) if a.file else fig       # a regenerated candidate, reviewed before it is copied
    print(loop.write_record("visual", fig.name, {
        "figure": str(fig), "reviewed_file": str(looked), "sha256": sha256_file(looked), "verdict": a.verdict,
        "summary": a.summary, "findings": json.loads(a.findings) if a.findings else [], "reviewer": "agent"}))
    return 0


def cmd_record_baseline(loop, a) -> int:
    entry = loop.registry()["baselines"][a.name]
    deviations = json.loads(a.deviations)
    for d in deviations:
        if not {"what", "official", "ours", "status"} <= set(d) or d["status"] not in ("justified", "open", "fixed"):
            raise SystemExit(f"bad deviation {d}: needs what/official/ours/status(justified|open|fixed)")
    if a.verdict == "aligned" and any(d["status"] == "open" for d in deviations):
        raise SystemExit('verdict "aligned" is not allowed while a deviation is open')
    print(loop.write_record("baseline", a.name, {
        "official": dict(entry["official"], commit=a.official_commit), "files": loop.baseline_files(entry),
        "verdict": a.verdict, "deviations": deviations, "summary": a.summary, "reviewer": "agent"}))
    return 0


def cmd_record_ablation(loop, a) -> int:
    entry = loop.registry()["ablations"][a.name]
    sanity = json.loads(a.sanity)
    unknown = set(sanity) - set(G.SANITY)
    if unknown:
        raise SystemExit(f"unknown sanity items {sorted(unknown)}; expected {sorted(G.SANITY)}")
    print(loop.write_record("ablation", a.name, {
        "question": entry["question"], "verdict": a.verdict, "sanity": sanity, "finding": a.finding,
        "related": json.loads(a.related) if a.related else [], "summary": a.summary, "reviewer": "agent"}))
    return 0


def cmd_packet(loop, a) -> int:
    rep = loop.report(results=not a.skip_results)
    out = loop.dir / "packets" / f"step{a.step}_{_dt.datetime.now():%Y%m%d_%H%M}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# Human review packet: step {a.step} ({G.now()})", "",
             "The agent has verified the items below. Open the files, judge them, then record your decision:", "",
             f'    uv run research-loop approve {a.step} --approver "<you>" --decision approve|reject '
             '--notes "..." --i-am-the-human', "",
             f"The approval binds to the current agent records (digest {G.digest(loop.step_records(a.step))[:12]}).",
             ""]
    for section in (("results", "visual", "baselines") if a.step == 2 else ("ablations",)):
        if section in rep:
            lines += [f"## {section}", "", "| item | state | note |", "|---|---|---|"]
            lines += [f"| {r[0]} | {r[1]} | {r[2].replace('|', '/')} |" for r in rep[section]] + [""]
    for kind in (("visual", "baseline") if a.step == 2 else ("ablation",)):
        for p in sorted((loop.reviews / kind).glob("*.json")):
            rec = json.loads(p.read_text())
            lines += [f"### {kind}: {p.stem} ({rec.get('verdict')})", "", rec.get("summary", ""), ""]
            if kind == "visual":
                lines += [f"- open: `{rec['figure']}`"] + [f"- finding: {f}" for f in rec.get("findings", [])]
            elif kind == "baseline":
                lines += [f"- official: {rec['official']['repo']} @ {rec['official'].get('commit')}"]
                lines += [f"- deviation [{d['status']}]: {d['what']}; official: {d['official']}; ours: {d['ours']}"
                          + (f"; why: {d['why']}" if d.get("why") else "") for d in rec.get("deviations", [])]
            else:
                lines += [f"- finding: {rec.get('finding', '')}"]
                lines += [f"- {k}: {'yes' if rec.get('sanity', {}).get(k) else 'NO'}" for k in G.SANITY]
            lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print(out)
    return 0


def cmd_approve(loop, a) -> int:
    if not a.i_am_the_human:
        raise SystemExit("approve is the human reviewer's action; pass --i-am-the-human to confirm")
    out = loop.reviews / "human" / f"step{a.step}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    records = loop.step_records(a.step)
    out.write_text(json.dumps({"step": a.step, "approver": a.approver, "decision": a.decision, "notes": a.notes,
                               "approved": G.now(), "bound_records": records, "bound_digest": G.digest(records)},
                              indent=1, sort_keys=True) + "\n")
    print(out)
    return 0


def cmd_log_attempt(loop, a) -> int:
    n = loop.log_attempt(hypothesis=a.hypothesis, change=a.change, command=a.command, seeds=a.seeds,
                         metric=a.metric, before=a.before, after=a.after, ci=a.ci, verdict=a.verdict, note=a.note)
    print(f"attempt {n} logged in {loop.log_path}")
    return 0


def cmd_budget(loop, a) -> int:
    loop.add_budget(a.phase, a.tokens, a.note)
    share = loop.budget()[1]
    print(f"verification share {100 * share:.0f}%")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="research-loop", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", help="project root (default: nearest parent with docs/research_loop)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status")
    s.add_argument("--verbose", action="store_true")
    s.add_argument("--skip-results", action="store_true")
    s.set_defaults(fn=cmd_status)
    s = sub.add_parser("gate")
    s.add_argument("step", type=int, choices=(2, 3, 4))
    s.add_argument("--skip-results", action="store_true")
    s.set_defaults(fn=cmd_gate)
    sub.add_parser("figures").set_defaults(fn=cmd_figures)

    s = sub.add_parser("record-visual")
    s.add_argument("figure")
    s.add_argument("--file", help="review this candidate (e.g. a regenerated PDF under runs/); OK once identical "
                                  "bytes are in the paper")
    s.add_argument("--verdict", required=True, choices=("pass", "fail"))
    s.add_argument("--summary", required=True)
    s.add_argument("--findings", help="JSON list of strings")
    s.set_defaults(fn=cmd_record_visual)
    s = sub.add_parser("record-baseline")
    s.add_argument("name")
    s.add_argument("--verdict", required=True, choices=("aligned", "deviates"))
    s.add_argument("--official-commit", required=True)
    s.add_argument("--deviations", required=True, help="JSON list of {what, official, ours, status, why}")
    s.add_argument("--summary", required=True)
    s.set_defaults(fn=cmd_record_baseline)
    s = sub.add_parser("record-ablation")
    s.add_argument("name")
    s.add_argument("--verdict", required=True, choices=("meaningful", "weak", "not_meaningful"))
    s.add_argument("--sanity", required=True, help="JSON {item: bool} over " + ", ".join(G.SANITY))
    s.add_argument("--finding", required=True)
    s.add_argument("--summary", required=True)
    s.add_argument("--related", help="optional JSON list of related-work notes (context only)")
    s.set_defaults(fn=cmd_record_ablation)

    s = sub.add_parser("packet")
    s.add_argument("step", type=int, choices=(2, 3))
    s.add_argument("--skip-results", action="store_true")
    s.set_defaults(fn=cmd_packet)
    s = sub.add_parser("approve")
    s.add_argument("step", type=int, choices=(2, 3))
    s.add_argument("--approver", required=True)
    s.add_argument("--decision", required=True, choices=("approve", "reject"))
    s.add_argument("--notes", default="")
    s.add_argument("--i-am-the-human", action="store_true")
    s.set_defaults(fn=cmd_approve)

    s = sub.add_parser("log-attempt")
    s.add_argument("--hypothesis", required=True, help="the mechanism you expect, not 'try X'")
    s.add_argument("--change", required=True, help="the ONE thing changed vs the kept state")
    s.add_argument("--verdict", required=True, choices=G.VERDICTS)
    for name in ("command", "seeds", "metric", "before", "after", "ci", "note"):
        s.add_argument(f"--{name}", default="")
    s.set_defaults(fn=cmd_log_attempt)
    s = sub.add_parser("budget")
    s.add_argument("--phase", required=True, choices=G.PHASES)
    s.add_argument("--tokens", required=True, type=int)
    s.add_argument("--note", default="")
    s.set_defaults(fn=cmd_budget)
    return p


def main(argv=None) -> int:
    a = build_parser().parse_args(argv)
    return a.fn(G.Loop(a.root), a)


if __name__ == "__main__":
    sys.exit(main())
