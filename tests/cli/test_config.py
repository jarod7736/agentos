import pytest
from pathlib import Path
from agentos.cli import main, resolve_home


def test_main_no_args_prints_help_and_exits_2(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2
    err = capsys.readouterr().err
    assert "usage:" in err.lower()


def test_main_help_flag_prints_help_and_exits_0(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    out = capsys.readouterr().out
    assert "usage:" in out.lower()


def test_resolve_home_uses_flag_when_given(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTOS_HOME", raising=False)
    result = resolve_home(flag=str(tmp_path))
    assert result == tmp_path


def test_resolve_home_falls_back_to_env(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path))
    result = resolve_home(flag=None)
    assert result == tmp_path


def test_resolve_home_flag_overrides_env(tmp_path, monkeypatch):
    flag_path = tmp_path / "from-flag"
    env_path = tmp_path / "from-env"
    monkeypatch.setenv("AGENTOS_HOME", str(env_path))
    result = resolve_home(flag=str(flag_path))
    assert result == flag_path


def test_resolve_home_defaults_to_user_home(monkeypatch):
    monkeypatch.delenv("AGENTOS_HOME", raising=False)
    result = resolve_home(flag=None)
    assert result == Path.home() / ".agentos"


from agentos.cli import resolve_project_id, ProjectResolutionError
from agentos.layer1.store import YamlContextStore


def test_resolve_project_flag_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTOS_PROJECT", "from-env")
    store = YamlContextStore(base_dir=tmp_path)
    store.create_project("Alpha", "x")
    assert resolve_project_id(flag="alpha", store=store) == "alpha"


def test_resolve_project_env_used_when_no_flag(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTOS_PROJECT", "alpha")
    store = YamlContextStore(base_dir=tmp_path)
    store.create_project("Alpha", "x")
    assert resolve_project_id(flag=None, store=store) == "alpha"


def test_resolve_project_single_project_default(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    store = YamlContextStore(base_dir=tmp_path)
    store.create_project("Solo", "x")
    assert resolve_project_id(flag=None, store=store) == "solo"


def test_resolve_project_raises_when_ambiguous(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    store = YamlContextStore(base_dir=tmp_path)
    store.create_project("Alpha", "x")
    store.create_project("Beta", "y")
    with pytest.raises(ProjectResolutionError) as excinfo:
        resolve_project_id(flag=None, store=store)
    assert "ambiguous" in str(excinfo.value).lower()


def test_resolve_project_raises_when_none_exist(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    store = YamlContextStore(base_dir=tmp_path)
    with pytest.raises(ProjectResolutionError) as excinfo:
        resolve_project_id(flag=None, store=store)
    assert "no projects" in str(excinfo.value).lower()
