# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**AgentOS** — an agent operating system that solves context switching. The core insight: humans and agents share the same problem — both start cold after a session boundary without persistent, structured project state. AgentOS provides that state as a first-class platform capability.

Built layer by layer, bottom-up. Each layer exposes a stable interface before the next is added. Never introduce cross-layer dependencies prematurely.

Always read `project.md` at the start of a session for current architecture state, decisions, and open questions. Use `/project` after any significant design conversation to keep it current.

## Architecture

### Layer 1 — Context/State Layer _(implemented)_
Owns persistent project state: current status, decision history, active focus, open questions. Exposes a read/write interface consumed by both humans and agents. Survives session boundaries.

The `agentos` CLI is the primary write surface — agents shell out to it at conversation boundaries; humans use it the same way.

### Layer 2 — Integration Layer _(planned)_
Bidirectional sync with external systems (2nd Brain Obsidian vault first). Layer 1 has zero knowledge of Layer 2 — integration is Layer 2's concern. See `project.md` for the sync design.

## Code Map

```
src/agentos/
  cli.py             # argparse CLI: project resolution, subcommand handlers, `main`
  layer1/
    model.py         # Pydantic models: Project, Goal, Decision, OpenQuestion
    codec.py         # Atomic YAML load/dump (write-to-temp, then replace)
    store.py         # ContextStore protocol + YamlContextStore implementation
tests/
  layer1/            # Store + codec tests
  cli/               # Per-subcommand tests + end-to-end smoke test
docs/superpowers/    # plans/ (implementation plans) and specs/ (design decisions)
.claude/agents/      # Sub-agent definitions used during development
.agentos-project     # Marker file (single line: `agentos`) — self-hosts this repo's state
project.md           # Current architecture state, decisions, open questions
```

### Data model (`layer1/model.py`)
- `Project` is the aggregate root: holds `goals`, `decisions`, `open_questions`, plus `status`, `active_goal_id`, `current_focus`.
- Ids are 8-char uuid4 slices, except `Project.id`, which is a slug of the name (lowercased, spaces → hyphens).
- Everything serializes with `model_dump(mode="json")`; timestamps are timezone-aware UTC.

### Storage (`layer1/store.py`, `layer1/codec.py`)
- One YAML file per project at `<home>/projects/<slug>.yaml`; `<home>` defaults to `~/.agentos`.
- Writes are atomic: `codec.dump` writes a `.tmp` sibling then `replace`s the target. Preserve this — never write the target file in place.
- The **decision log is append-only**. Decisions are never overwritten or deleted. A reversal is a new decision that supersedes the old one. `question resolve` records the answer as a new decision, then removes the question.

### CLI (`cli.py`)
- Verbs: `project {init,show}`, `goal {add,complete}`, `decision add`, `focus set`, `question {add,resolve}`.
- Global flags: `--home` (overrides `AGENTOS_HOME`), `--project` (overrides `AGENTOS_PROJECT`), `--json`.
- **Project resolution** (priority order): `--project` flag → `AGENTOS_PROJECT` env → `.agentos-project` marker walked up from cwd → the sole project if only one exists → else `ProjectResolutionError`.
- Handlers return an exit code and print via `_emit` (JSON when `--json`, else `render_project_text`). Raise `NotFoundError` / `ProjectResolutionError` for user errors; `main` catches them and prints `error: …` to stderr with exit 1.

## Working Principles

**Think Before Coding**
- Before you answer, tell me what you need to know to answer well, and point out any assumptions you'd otherwise make.
- State assumptions explicitly; never assume silently.
- If multiple interpretations exist, present them rather than picking one.
- If a simpler approach exists or the request is flawed, say so.
- If confused, name what is unclear rather than guessing.

**Simplicity First**
- Write the minimum code that solves the problem.
- No speculative code, future-proofing, or unasked-for features.
- No unnecessary abstractions, config files, or enterprise patterns for simple tasks.

**Surgical Changes**
- Edit only the necessary code.
- Match existing style, even if imperfect.
- Do not clean up adjacent code that isn't broken.

**Goal-Driven Execution**
- Define success criteria before writing code.
- Prefer test-driven development: write a failing test first, then make it pass.

## Sub-Agents

Specialized agents live in `.claude/agents/`. Use them in order for any new layer:

| Agent | Use for |
|---|---|
| `architect` | Layer design, interface contracts, ADRs |
| `data-engineer` | Storage format, serialization, schema evolution |
| `quality-engineer` | Test strategy, success criteria, edge cases |
| `software-engineer` | Implementation (after interface + tests exist) |
| `ui-ux-engineer` | CLI design, command structure, error messages |
| `communications-expert` | ADRs, README, PR descriptions, `project.md` updates |

## Commands

```bash
uv run pytest                        # all tests
uv run pytest tests/layer1/ -v       # layer 1 only
uv run pytest tests/cli/ -v          # CLI only
uv run pytest -k "test_name"         # single test

uv run agentos project show          # exercise the CLI (add --json for machine output)
```

Requires Python 3.12+ and [`uv`](https://docs.astral.sh/uv/). Runtime deps: `pydantic>=2.7`, `ruamel-yaml>=0.18`. The `agentos` console script is defined in `pyproject.toml` (`agentos.cli:main`).
