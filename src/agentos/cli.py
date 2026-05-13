"""agentos command-line interface."""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

from agentos.layer1.model import Project
from agentos.layer1.store import YamlContextStore


def resolve_home(flag: str | None) -> Path:
    if flag:
        return Path(flag)
    env = os.environ.get("AGENTOS_HOME")
    if env:
        return Path(env)
    return Path.home() / ".agentos"


class ProjectResolutionError(Exception):
    """Raised when the current project cannot be determined unambiguously."""


def resolve_project_id(flag: str | None, store: YamlContextStore) -> str:
    if flag:
        return flag
    env = os.environ.get("AGENTOS_PROJECT")
    if env:
        return env
    projects = store.list_projects()
    if len(projects) == 1:
        return projects[0].id
    if not projects:
        raise ProjectResolutionError(
            "No projects exist. Run `agentos project init <name>` first."
        )
    slugs = ", ".join(p.id for p in projects)
    raise ProjectResolutionError(
        f"Project is ambiguous (existing: {slugs}). "
        "Pass --project <slug> or set AGENTOS_PROJECT."
    )


def _emit(args: argparse.Namespace, obj: dict, text: str) -> None:
    if args.json:
        print(json.dumps(obj))
    else:
        print(text)


def render_project_text(p: Project) -> str:
    lines = [
        f"# {p.name} ({p.id})",
        p.description or "(no description)",
        "",
        f"Status: {p.status}",
        f"Focus: {p.current_focus or '(none)'}",
        "",
        f"Goals ({len(p.goals)}):",
    ]
    for g in p.goals:
        marker = "x" if g.status == "completed" else " "
        active = " *" if p.active_goal_id == g.id else ""
        lines.append(f"  [{marker}] {g.id} {g.title}{active}")
    if not p.goals:
        lines.append("  (none)")
    lines.append("")
    lines.append(f"Decisions ({len(p.decisions)}):")
    for d in p.decisions:
        lines.append(f"  - {d.id} {d.title}")
        lines.append(f"      rationale: {d.rationale}")
    if not p.decisions:
        lines.append("  (none)")
    lines.append("")
    lines.append(f"Open questions ({len(p.open_questions)}):")
    for q in p.open_questions:
        lines.append(f"  ? {q.id} {q.question}")
    if not p.open_questions:
        lines.append("  (none)")
    return "\n".join(lines)


def cmd_project_show(args: argparse.Namespace, store: YamlContextStore) -> int:
    project_id = resolve_project_id(args.project, store)
    project = store.get_project(project_id)
    if project is None:
        print(f"error: project '{project_id}' not found", file=sys.stderr)
        return 1
    _emit(args, project.model_dump(mode="json"), render_project_text(project))
    return 0


def cmd_project_init(args: argparse.Namespace, store: YamlContextStore) -> int:
    project = store.create_project(args.name, args.description)
    _emit(
        args,
        project.model_dump(mode="json"),
        f"Created project '{project.id}'.",
    )
    return 0


def cmd_goal_add(args: argparse.Namespace, store: YamlContextStore) -> int:
    project_id = resolve_project_id(args.project, store)
    goal = store.add_goal(project_id, args.title, args.description)
    _emit(args, goal.model_dump(mode="json"), f"Added goal {goal.id}: {goal.title}")
    return 0


def cmd_goal_complete(args: argparse.Namespace, store: YamlContextStore) -> int:
    project_id = resolve_project_id(args.project, store)
    goal = store.complete_goal(project_id, args.goal_id)
    _emit(args, goal.model_dump(mode="json"), f"Completed goal {goal.id}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentos",
        description="Persistent project context for humans and agents.",
    )
    parser.add_argument("--home", help="AgentOS state directory (overrides AGENTOS_HOME).")
    parser.add_argument("--project", help="Project slug (overrides AGENTOS_PROJECT).")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    sub = parser.add_subparsers(dest="command", required=True)

    project_p = sub.add_parser("project", help="Manage projects.")
    project_sub = project_p.add_subparsers(dest="project_cmd", required=True)

    init_p = project_sub.add_parser("init", help="Create a new project.")
    init_p.add_argument("name", help="Human-readable project name (slugified for the id).")
    init_p.add_argument("--description", default="", help="Short description.")
    init_p.set_defaults(handler=cmd_project_init)

    show_p = project_sub.add_parser("show", help="Print project state.")
    show_p.set_defaults(handler=cmd_project_show)

    goal_p = sub.add_parser("goal", help="Manage goals.")
    goal_sub = goal_p.add_subparsers(dest="goal_cmd", required=True)

    goal_add_p = goal_sub.add_parser("add", help="Add a goal.")
    goal_add_p.add_argument("title")
    goal_add_p.add_argument("--description", default=None)
    goal_add_p.set_defaults(handler=cmd_goal_add)

    goal_complete_p = goal_sub.add_parser("complete", help="Mark a goal complete.")
    goal_complete_p.add_argument("goal_id")
    goal_complete_p.set_defaults(handler=cmd_goal_complete)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    home = resolve_home(args.home)
    store = YamlContextStore(base_dir=home)
    try:
        return args.handler(args, store)
    except ProjectResolutionError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
