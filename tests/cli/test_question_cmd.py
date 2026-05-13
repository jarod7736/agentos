import json
import pytest
from agentos.cli import main


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path))
    main(["project", "init", "AgentOS", "--description", "x"])
    return tmp_path


def test_question_add_appears_in_project(home, capsys):
    capsys.readouterr()
    main(["question", "add", "Deployment model?"])
    capsys.readouterr()
    main(["--json", "project", "show"])
    project = json.loads(capsys.readouterr().out)
    assert len(project["open_questions"]) == 1
    assert project["open_questions"][0]["question"] == "Deployment model?"


def test_question_resolve_removes_question_and_appends_decision(home, capsys):
    capsys.readouterr()
    main(["--json", "question", "add", "Deployment model?"])
    qid = json.loads(capsys.readouterr().out)["id"]

    code = main(["question", "resolve", qid, "Local + git sync"])
    assert code == 0

    capsys.readouterr()
    main(["--json", "project", "show"])
    project = json.loads(capsys.readouterr().out)
    assert project["open_questions"] == []
    assert len(project["decisions"]) == 1
    decision = project["decisions"][0]
    assert "Deployment model?" in decision["title"]
    assert decision["rationale"] == "Local + git sync"


def test_question_resolve_unknown_id_errors(home, capsys):
    code = main(["question", "resolve", "bogus", "answer"])
    assert code == 1
    err = capsys.readouterr().err
    assert "not found" in err.lower()
