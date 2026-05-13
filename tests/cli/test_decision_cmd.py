import json
import pytest
from agentos.cli import main


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path))
    main(["project", "init", "AgentOS", "--description", "x"])
    return tmp_path


def test_decision_add_minimum_args(home, capsys):
    capsys.readouterr()
    code = main([
        "decision", "add", "Use YAML storage",
        "--rationale", "Human-readable and portable.",
    ])
    assert code == 0
    capsys.readouterr()
    main(["--json", "project", "show"])
    project = json.loads(capsys.readouterr().out)
    assert len(project["decisions"]) == 1
    assert project["decisions"][0]["title"] == "Use YAML storage"
    assert project["decisions"][0]["rationale"] == "Human-readable and portable."


def test_decision_add_with_alternatives(home, capsys):
    capsys.readouterr()
    main([
        "decision", "add", "Use YAML storage",
        "--rationale", "x",
        "--alternative", "SQLite",
        "--alternative", "JSON",
    ])
    capsys.readouterr()
    main(["--json", "project", "show"])
    project = json.loads(capsys.readouterr().out)
    assert project["decisions"][0]["alternatives"] == ["SQLite", "JSON"]


def test_decision_add_is_append_only(home, capsys):
    capsys.readouterr()
    main(["decision", "add", "First", "--rationale", "a"])
    main(["decision", "add", "Second", "--rationale", "b"])
    capsys.readouterr()
    main(["--json", "project", "show"])
    project = json.loads(capsys.readouterr().out)
    titles = [d["title"] for d in project["decisions"]]
    assert titles == ["First", "Second"]
