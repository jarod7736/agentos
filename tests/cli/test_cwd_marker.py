"""Project discovery from a `.agentos-project` marker walked up from cwd."""
import json
import pytest

from agentos.cli import (
    PROJECT_MARKER,
    ProjectResolutionError,
    main,
    resolve_project_id,
)
from agentos.layer1.store import YamlContextStore


def test_resolve_uses_marker_in_cwd(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    store = YamlContextStore(base_dir=tmp_path / "home")
    store.create_project("Alpha", "x")
    store.create_project("Beta", "y")
    work = tmp_path / "work"
    work.mkdir()
    (work / PROJECT_MARKER).write_text("alpha\n")
    assert resolve_project_id(flag=None, store=store, cwd=work) == "alpha"


def test_resolve_walks_up_from_subdirectory(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    store = YamlContextStore(base_dir=tmp_path / "home")
    store.create_project("Alpha", "x")
    store.create_project("Beta", "y")
    repo = tmp_path / "repo"
    deep = repo / "src" / "nested"
    deep.mkdir(parents=True)
    (repo / PROJECT_MARKER).write_text("beta")
    assert resolve_project_id(flag=None, store=store, cwd=deep) == "beta"


def test_resolve_flag_beats_marker(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    store = YamlContextStore(base_dir=tmp_path / "home")
    store.create_project("Alpha", "x")
    work = tmp_path / "work"
    work.mkdir()
    (work / PROJECT_MARKER).write_text("from-marker")
    assert resolve_project_id(flag="from-flag", store=store, cwd=work) == "from-flag"


def test_resolve_env_beats_marker(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTOS_PROJECT", "from-env")
    store = YamlContextStore(base_dir=tmp_path / "home")
    store.create_project("Alpha", "x")
    work = tmp_path / "work"
    work.mkdir()
    (work / PROJECT_MARKER).write_text("from-marker")
    assert resolve_project_id(flag=None, store=store, cwd=work) == "from-env"


def test_resolve_marker_beats_single_project_default(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    store = YamlContextStore(base_dir=tmp_path / "home")
    store.create_project("Solo", "x")
    work = tmp_path / "work"
    work.mkdir()
    (work / PROJECT_MARKER).write_text("explicit")
    assert resolve_project_id(flag=None, store=store, cwd=work) == "explicit"


def test_resolve_marker_beats_ambiguity(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    store = YamlContextStore(base_dir=tmp_path / "home")
    store.create_project("Alpha", "x")
    store.create_project("Beta", "y")
    work = tmp_path / "work"
    work.mkdir()
    (work / PROJECT_MARKER).write_text("alpha")
    assert resolve_project_id(flag=None, store=store, cwd=work) == "alpha"


def test_resolve_blank_marker_falls_through(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    store = YamlContextStore(base_dir=tmp_path / "home")
    store.create_project("Solo", "x")
    work = tmp_path / "work"
    work.mkdir()
    (work / PROJECT_MARKER).write_text("   \n")
    assert resolve_project_id(flag=None, store=store, cwd=work) == "solo"


def test_resolve_no_marker_falls_through(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    store = YamlContextStore(base_dir=tmp_path / "home")
    store.create_project("Solo", "x")
    work = tmp_path / "work"
    work.mkdir()
    assert resolve_project_id(flag=None, store=store, cwd=work) == "solo"


def test_resolve_cwd_none_skips_walk(tmp_path, monkeypatch):
    """Backwards-compat: callers that pass cwd=None get pre-existing behavior."""
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    store = YamlContextStore(base_dir=tmp_path / "home")
    store.create_project("Alpha", "x")
    store.create_project("Beta", "y")
    with pytest.raises(ProjectResolutionError):
        resolve_project_id(flag=None, store=store, cwd=None)


def test_resolve_ambiguity_message_mentions_marker(tmp_path, monkeypatch):
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    store = YamlContextStore(base_dir=tmp_path / "home")
    store.create_project("Alpha", "x")
    store.create_project("Beta", "y")
    work = tmp_path / "work"
    work.mkdir()
    with pytest.raises(ProjectResolutionError) as excinfo:
        resolve_project_id(flag=None, store=store, cwd=work)
    msg = str(excinfo.value).lower()
    assert ".agentos-project" in msg


def test_main_uses_cwd_marker_end_to_end(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("AGENTOS_HOME", str(tmp_path / "home"))
    monkeypatch.delenv("AGENTOS_PROJECT", raising=False)
    main(["project", "init", "Alpha"])
    main(["project", "init", "Beta"])
    capsys.readouterr()

    work = tmp_path / "checkout"
    work.mkdir()
    (work / PROJECT_MARKER).write_text("beta\n")
    monkeypatch.chdir(work)

    main(["--json", "project", "show"])
    project = json.loads(capsys.readouterr().out)
    assert project["id"] == "beta"
