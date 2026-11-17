"""Gate behaviour of the research loop: hash binding, staleness, human-only approval, ablation sanity."""

import json

import pytest

from airesearch.loop import cli
from airesearch.loop import gates as G


@pytest.fixture
def project(tmp_path):
    (tmp_path / "paper/figures").mkdir(parents=True)
    (tmp_path / "paper/figures/a.pdf").write_bytes(b"figure a")
    (tmp_path / "paper/main.tex").write_text(
        "\\includegraphics[width=1in]{figures/a.pdf}\n% \\includegraphics{figures/commented.pdf}\n")
    (tmp_path / "baseline.py").write_text("x = 1\n")
    (tmp_path / "runs/exp/r0").mkdir(parents=True)
    (tmp_path / "runs/exp/r0/result.json").write_text("{}")
    loop_dir = tmp_path / "docs/research_loop"
    loop_dir.mkdir(parents=True)
    (loop_dir / "registry.json").write_text(json.dumps({
        "manuscript": "paper",
        "results": [{"name": "exp", "glob": "runs/exp/*/result.json", "min_count": 1}],
        "baselines": {"B": {"official": {"repo": "https://example.org/b"}, "our_code": ["baseline.py"]}},
        "ablations": {"X": {"question": "does X matter?"}},
    }))
    return tmp_path


def run(project, *args):
    return cli.main(["--root", str(project), *args])


def report(project):
    return G.Loop(project).report()


def states(rows):
    return {k: s for k, s, _ in rows}


ALL_SANE = json.dumps(dict.fromkeys(G.SANITY, True))
DEV = json.dumps([{"what": "w", "official": "o", "ours": "u", "status": "justified", "why": "y"}])


def approve(project, step):
    run(project, "approve", str(step), "--approver", "me", "--decision", "approve", "--i-am-the-human")


def verify_everything(project):
    run(project, "record-visual", "a.pdf", "--verdict", "pass", "--summary", "looked")
    run(project, "record-baseline", "B", "--verdict", "aligned", "--official-commit", "abc", "--deviations", DEV,
        "--summary", "s")
    run(project, "record-ablation", "X", "--verdict", "meaningful", "--sanity", ALL_SANE, "--finding", "f",
        "--summary", "s")


def test_commented_figures_are_ignored(project):
    assert [p.name for p in G.Loop(project).paper_figures()] == ["a.pdf"]


def test_gates_need_agent_records_then_human_approval(project):
    assert not G.gate_open(report(project), 4)
    verify_everything(project)
    r = report(project)
    assert r["human2"][0][1] == "PENDING" and not G.gate_open(r, 2)
    with pytest.raises(SystemExit):           # the approval is the human's action
        run(project, "approve", "2", "--approver", "me", "--decision", "approve")
    approve(project, 2)
    approve(project, 3)
    assert G.gate_open(report(project), 4)


def test_regenerated_figure_reopens_review_and_approval(project):
    verify_everything(project)
    approve(project, 2)
    (project / "paper/figures/a.pdf").write_bytes(b"figure a, regenerated")
    r = report(project)
    assert states(r["visual"])["a.pdf"] == "STALE" and not G.gate_open(r, 2)
    run(project, "record-visual", "a.pdf", "--verdict", "pass", "--summary", "looked again")
    assert report(project)["human2"][0][1] == "STALE"     # approval was bound to the old records


def test_candidate_review_turns_ok_once_copied(project):
    cand = project / "candidate.pdf"
    cand.write_bytes(b"new figure")
    run(project, "record-visual", "a.pdf", "--file", str(cand), "--verdict", "pass", "--summary", "s")
    assert states(report(project)["visual"])["a.pdf"] == "STALE"
    (project / "paper/figures/a.pdf").write_bytes(cand.read_bytes())
    assert states(report(project)["visual"])["a.pdf"] == "OK"


def test_editing_baseline_code_reopens_fidelity_review(project):
    verify_everything(project)
    (project / "baseline.py").write_text("x = 2\n")
    assert states(report(project)["baselines"])["B"] == "STALE"


def test_aligned_with_open_deviation_is_refused(project):
    dev = json.dumps([{"what": "w", "official": "o", "ours": "u", "status": "open"}])
    with pytest.raises(SystemExit):
        run(project, "record-baseline", "B", "--verdict", "aligned", "--official-commit", "abc", "--deviations",
            dev, "--summary", "s")


def test_ablation_needs_every_sanity_item(project):
    partial = dict.fromkeys(G.SANITY, True) | {"reference_reproduced": False}
    run(project, "record-ablation", "X", "--verdict", "meaningful", "--sanity", json.dumps(partial),
        "--finding", "f", "--summary", "s")
    assert states(report(project)["ablations"])["X"] == "FAIL"


def test_missing_results_or_no_figures_keep_gate_closed(project):
    verify_everything(project)
    approve(project, 2)
    approve(project, 3)
    (project / "runs/exp/r0/result.json").unlink()
    assert not G.gate_open(report(project), 2)
    (project / "runs/exp/r0/result.json").write_text("{}")
    (project / "paper/main.tex").write_text("no figures yet\n")
    assert not G.gate_open(report(project), 4)


def test_experiment_log_and_budget(project):
    loop = G.Loop(project)
    assert loop.log_attempt(hypothesis="h", change="c", verdict="kept") == 1
    assert loop.log_attempt(hypothesis="h2", change="c2", verdict="reverted") == 2
    with pytest.raises(ValueError):
        loop.log_attempt(hypothesis="h", change="c", verdict="maybe")
    rows = loop.log_path.read_text().splitlines()
    assert rows[0].split("\t") == list(G.LOG_COLUMNS) and rows[2].split("\t")[-2] == "reverted"
    loop.add_budget("build", 300)
    loop.add_budget("verify", 700)
    assert loop.budget()[1] == pytest.approx(0.7)
