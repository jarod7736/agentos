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


def test_project_show_text_includes_name_and_description(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path))
    main(["project", "init", "AgentOS", "--description", "Agent OS"])
    capsys.readouterr()
    code = main(["project", "show"])
    assert code == 0
    out = capsys.readouterr().out
    assert "AgentOS" in out
    assert "Agent OS" in out


def test_project_show_with_explicit_slug(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path))
    main(["project", "init", "Alpha", "--description", "A"])
    main(["project", "init", "Beta", "--description", "B"])
    capsys.readouterr()
    code = main(["--project", "beta", "project", "show"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Beta" in out
    assert "Alpha" not in out


def test_project_show_no_projects_errors_exit_1(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path))
    code = main(["project", "show"])
    assert code == 1
    err = capsys.readouterr().err
    assert "no projects" in err.lower()
