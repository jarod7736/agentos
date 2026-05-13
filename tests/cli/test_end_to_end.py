"""End-to-end smoke: a realistic agent session populates a project."""
import json
import pytest
from agentos.cli import main


def test_full_session_round_trip(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path))

    # Bootstrap.
    main(["project", "init", "AgentOS", "--description", "Agent OS"])

    # Capture the goal id.
    capsys.readouterr()
    main(["--json", "goal", "add", "Ship the CLI"])
    goal_id = json.loads(capsys.readouterr().out)["id"]

    # Capture the question id.
    main(["--json", "question", "add", "Which CLI framework?"])
    question_id = json.loads(capsys.readouterr().out)["id"]

    # Record progress.
    main(["focus", "set", "Wiring up subcommands"])
    main([
        "decision", "add", "Use argparse",
        "--rationale", "Stdlib, zero new deps.",
        "--alternative", "click",
        "--alternative", "typer",
    ])
    main(["question", "resolve", question_id, "argparse"])
    main(["goal", "complete", goal_id])

    # Verify final state.
    capsys.readouterr()
    main(["--json", "project", "show"])
    project = json.loads(capsys.readouterr().out)

    assert project["current_focus"] == "Wiring up subcommands"
    assert project["open_questions"] == []
    decision_titles = [d["title"] for d in project["decisions"]]
    assert "Use argparse" in decision_titles
    assert any(t.startswith("Answered:") for t in decision_titles)
    goal = next(g for g in project["goals"] if g["id"] == goal_id)
    assert goal["status"] == "completed"
