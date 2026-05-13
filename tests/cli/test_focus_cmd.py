import json
import pytest
from agentos.cli import main


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path))
    main(["project", "init", "AgentOS", "--description", "x"])
    return tmp_path


def test_focus_set_updates_project(home, capsys):
    capsys.readouterr()
    code = main(["focus", "set", "Shipping the v1 CLI"])
    assert code == 0
    capsys.readouterr()
    main(["--json", "project", "show"])
    project = json.loads(capsys.readouterr().out)
    assert project["current_focus"] == "Shipping the v1 CLI"


def test_focus_set_replaces_previous(home, capsys):
    main(["focus", "set", "First"])
    main(["focus", "set", "Second"])
    capsys.readouterr()
    main(["--json", "project", "show"])
    project = json.loads(capsys.readouterr().out)
    assert project["current_focus"] == "Second"
