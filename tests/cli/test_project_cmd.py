import json
import pytest
from agentos.cli import main


def test_project_init_creates_yaml_file(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path))
    code = main(["project", "init", "AgentOS", "--description", "Agent operating system"])
    assert code == 0
    assert (tmp_path / "projects" / "agentos.yaml").exists()


def test_project_init_prints_slug(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path))
    main(["project", "init", "AgentOS", "--description", "desc"])
    out = capsys.readouterr().out
    assert "agentos" in out


def test_project_init_json_output(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path))
    main(["--json", "project", "init", "AgentOS", "--description", "desc"])
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["id"] == "agentos"
    assert payload["name"] == "AgentOS"
