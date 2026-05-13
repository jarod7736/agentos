"""agentos command-line interface."""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path


def resolve_home(flag: str | None) -> Path:
    if flag:
        return Path(flag)
    env = os.environ.get("AGENTOS_HOME")
    if env:
        return Path(env)
    return Path.home() / ".agentos"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentos",
        description="Persistent project context for humans and agents.",
    )
    parser.add_argument(
        "--home",
        help="AgentOS state directory (overrides AGENTOS_HOME; default ~/.agentos).",
    )
    parser.add_argument(
        "--project",
        help="Project slug (overrides AGENTOS_PROJECT; defaults to the single existing project).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output.",
    )
    parser.add_subparsers(dest="command", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv if argv is not None else sys.argv[1:])
    return 0


if __name__ == "__main__":
    sys.exit(main())
