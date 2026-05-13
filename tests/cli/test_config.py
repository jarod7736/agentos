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
