import json
import pytest
from agentos.cli import main


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path))
    main(["project", "init", "AgentOS", "--description", "x"])
    return tmp_path


def test_goal_add_appears_in_project(home, capsys):
    capsys.readouterr()
    code = main(["goal", "add", "Ship the CLI"])
    assert code == 0
    capsys.readouterr()
    main(["project", "show"])
    out = capsys.readouterr().out
    assert "Ship the CLI" in out


def test_goal_add_json_returns_id(home, capsys):
    capsys.readouterr()
    main(["--json", "goal", "add", "Ship the CLI"])
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["title"] == "Ship the CLI"
    assert "id" in payload


def test_goal_complete_marks_completed(home, capsys):
    capsys.readouterr()
    main(["--json", "goal", "add", "Ship the CLI"])
    goal_id = json.loads(capsys.readouterr().out)["id"]
    code = main(["goal", "complete", goal_id])
    assert code == 0
    capsys.readouterr()
    main(["--json", "project", "show"])
    project = json.loads(capsys.readouterr().out)
    goal = next(g for g in project["goals"] if g["id"] == goal_id)
    assert goal["status"] == "completed"


def test_goal_complete_unknown_id_errors(home, capsys):
    code = main(["goal", "complete", "bogus"])
    assert code == 1
    err = capsys.readouterr().err
    assert "not found" in err.lower()
