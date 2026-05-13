"""agentos command-line interface."""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

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


def cmd_project_init(args: argparse.Namespace, store: YamlContextStore) -> int:
    project = store.create_project(args.name, args.description)
    _emit(
        args,
        project.model_dump(mode="json"),
        f"Created project '{project.id}'.",
    )
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
