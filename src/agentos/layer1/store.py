from pathlib import Path
from typing import Protocol
from ruamel.yaml import YAML
from .model import Decision, Goal, OpenQuestion, Project
from . import codec

_yaml = YAML()


class ContextStore(Protocol):
    def create_project(self, name: str, description: str) -> Project: ...
    def get_project(self, id: str) -> Project | None: ...
    def list_projects(self) -> list[Project]: ...
    def add_goal(self, project_id: str, title: str, description: str | None = None) -> Goal: ...
    def set_active_goal(self, project_id: str, goal_id: str) -> Project: ...
    def complete_goal(self, project_id: str, goal_id: str) -> Goal: ...
    def record_decision(self, project_id: str, title: str, rationale: str, alternatives: list[str]) -> Decision: ...
    def add_open_question(self, project_id: str, question: str, options: list[str]) -> OpenQuestion: ...
    def resolve_question(self, project_id: str, question_id: str) -> None: ...
    def current_context(self) -> Project | None: ...
    def switch_project(self, id: str) -> Project | None: ...


def _slug(name: str) -> str:
    return name.lower().replace(" ", "-")


class YamlContextStore:
    def __init__(self, base_dir: Path | None = None) -> None:
        self._base = base_dir or Path.home() / ".agentos"
        self._projects_dir = self._base / "projects"
        self._current_file = self._base / "current.yaml"

    def _path(self, project_id: str) -> Path:
        return self._projects_dir / f"{project_id}.yaml"

    def _load(self, project_id: str) -> Project | None:
        path = self._path(project_id)
        if not path.exists():
            return None
        return codec.load(path)

    def _save(self, project: Project) -> None:
        codec.dump(project, self._path(project.id))

    def create_project(self, name: str, description: str) -> Project:
        project = Project(id=_slug(name), name=name, description=description)
        self._save(project)
        return project

    def get_project(self, id: str) -> Project | None:
        return self._load(id)

    def list_projects(self) -> list[Project]:
        if not self._projects_dir.exists():
            return []
        return [codec.load(p) for p in sorted(self._projects_dir.glob("*.yaml"))]

    def add_goal(self, project_id: str, title: str, description: str | None = None) -> Goal:
        project = self._load(project_id)
        goal = Goal(title=title, description=description)
        project.goals.append(goal)
        self._save(project)
        return goal

    def set_active_goal(self, project_id: str, goal_id: str) -> Project:
        project = self._load(project_id)
        project.active_goal_id = goal_id
        self._save(project)
        return project

    def complete_goal(self, project_id: str, goal_id: str) -> Goal:
        project = self._load(project_id)
        goal = next(g for g in project.goals if g.id == goal_id)
        goal.status = "completed"
        self._save(project)
        return goal

    def record_decision(self, project_id: str, title: str, rationale: str, alternatives: list[str]) -> Decision:
        project = self._load(project_id)
        decision = Decision(title=title, rationale=rationale, alternatives=alternatives)
        project.decisions.append(decision)
        self._save(project)
        return decision

    def add_open_question(self, project_id: str, question: str, options: list[str]) -> OpenQuestion:
        project = self._load(project_id)
        oq = OpenQuestion(question=question, options=options)
        project.open_questions.append(oq)
        self._save(project)
        return oq

    def resolve_question(self, project_id: str, question_id: str) -> None:
        project = self._load(project_id)
        project.open_questions = [q for q in project.open_questions if q.id != question_id]
        self._save(project)

    def current_context(self) -> Project | None:
        if not self._current_file.exists():
            return None
        with self._current_file.open("r") as f:
            data = _yaml.load(f)
        if not data or "current" not in data:
            return None
        return self._load(data["current"])

    def switch_project(self, id: str) -> Project | None:
        project = self._load(id)
        if project is None:
            return None
        self._current_file.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._current_file.with_suffix(".tmp")
        with tmp.open("w") as f:
            _yaml.dump({"current": id}, f)
        tmp.replace(self._current_file)
        return project
