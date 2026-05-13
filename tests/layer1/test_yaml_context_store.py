import pytest
from pathlib import Path
from agentos.layer1.store import YamlContextStore


@pytest.fixture
def store(tmp_path: Path) -> YamlContextStore:
    return YamlContextStore(base_dir=tmp_path)


# --- create_project ---

def test_create_project_returns_project(store):
    p = store.create_project("AgentOS", "Agent operating system")
    assert p.name == "AgentOS"
    assert p.id == "agentos"
    assert p.status == "active"


def test_create_project_writes_yaml_file(store, tmp_path):
    store.create_project("AgentOS", "Agent operating system")
    assert (tmp_path / "projects" / "agentos.yaml").exists()


# --- get_project ---

def test_get_project_returns_saved_project(store):
    store.create_project("AgentOS", "Agent operating system")
    p = store.get_project("agentos")
    assert p is not None
    assert p.name == "AgentOS"


def test_get_project_returns_none_for_missing(store):
    assert store.get_project("nonexistent") is None


# --- list_projects ---

def test_list_projects_returns_all(store):
    store.create_project("Alpha", "First")
    store.create_project("Beta", "Second")
    projects = store.list_projects()
    assert len(projects) == 2
    ids = {p.id for p in projects}
    assert ids == {"alpha", "beta"}


def test_list_projects_returns_empty_when_none(store):
    assert store.list_projects() == []


# --- add_goal / set_active_goal ---

def test_add_goal_appears_in_project(store):
    store.create_project("AgentOS", "desc")
    goal = store.add_goal("agentos", "Design Layer 1")
    p = store.get_project("agentos")
    assert len(p.goals) == 1
    assert p.goals[0].id == goal.id


def test_set_active_goal_updates_project(store):
    store.create_project("AgentOS", "desc")
    goal = store.add_goal("agentos", "Design Layer 1")
    p = store.set_active_goal("agentos", goal.id)
    assert p.active_goal_id == goal.id


# --- record_decision ---

def test_record_decision_appended_to_project(store):
    store.create_project("AgentOS", "desc")
    store.record_decision("agentos", "Use YAML storage", "Human-readable and portable", ["SQLite", "JSON"])
    p = store.get_project("agentos")
    assert len(p.decisions) == 1
    assert p.decisions[0].title == "Use YAML storage"


def test_record_decision_preserves_existing_decisions(store):
    store.create_project("AgentOS", "desc")
    store.record_decision("agentos", "Decision One", "Reason one", [])
    store.record_decision("agentos", "Decision Two", "Reason two", [])
    p = store.get_project("agentos")
    assert len(p.decisions) == 2
    assert p.decisions[0].title == "Decision One"
    assert p.decisions[1].title == "Decision Two"


# --- switch_project / current_context ---

def test_switch_project_sets_current(store):
    store.create_project("AgentOS", "desc")
    p = store.switch_project("agentos")
    assert p is not None
    assert p.id == "agentos"


def test_current_context_returns_active_project(store):
    store.create_project("AgentOS", "desc")
    store.switch_project("agentos")
    p = store.current_context()
    assert p is not None
    assert p.id == "agentos"


def test_current_context_returns_none_when_no_active(store):
    assert store.current_context() is None


def test_switch_project_returns_none_for_missing(store):
    assert store.switch_project("nonexistent") is None


# --- set_focus / current_focus ---

def test_set_focus_updates_project(store):
    store.create_project("AgentOS", "desc")
    p = store.set_focus("agentos", "Shipping the Layer 1 CLI")
    assert p.current_focus == "Shipping the Layer 1 CLI"


def test_set_focus_persists_across_reload(store):
    store.create_project("AgentOS", "desc")
    store.set_focus("agentos", "First focus")
    reloaded = store.get_project("agentos")
    assert reloaded.current_focus == "First focus"


def test_set_focus_replaces_previous_value(store):
    store.create_project("AgentOS", "desc")
    store.set_focus("agentos", "First focus")
    store.set_focus("agentos", "Second focus")
    p = store.get_project("agentos")
    assert p.current_focus == "Second focus"


def test_new_project_has_no_focus(store):
    p = store.create_project("AgentOS", "desc")
    assert p.current_focus is None
