# AgentOS

An agent operating system that solves context switching.

Humans and agents share the same problem: both start cold after a session boundary without persistent, structured project state. AgentOS provides that state as a first-class platform capability — making re-entry instant rather than expensive.

## Status

Built bottom-up, one layer at a time. Each layer exposes a stable interface before the next is added.

| Layer | What it owns | Status |
| --- | --- | --- |
| **1. Context/State** | Persistent project state — current status, decision history, active focus, open questions | Implemented. CLI v1 ships `agentos {project,goal,decision,focus,question}` verbs. |
| **2. Integration** | Bidirectional sync with external systems (2nd Brain first) | Planned |

Deployment is local-first with user-managed git sync. Population is agent-assisted via an `agentos` CLI; agents write at conversation boundaries. See [docs/superpowers/specs/2026-05-12-layer1-deployment-and-population-design.md](docs/superpowers/specs/2026-05-12-layer1-deployment-and-population-design.md) for the full design.

## Usage

The `agentos` CLI is the primary write surface — agents shell out to it at conversation boundaries; humans use it the same way.

````bash
# Bootstrap
agentos project init "AgentOS" --description "Agent operating system"

# Capture state as it changes
agentos goal add "Ship the v1 CLI"
agentos focus set "Wiring up subcommands"
agentos decision add "Use argparse" --rationale "Stdlib, no new deps" --alternative click --alternative typer
agentos question add "Deployment model?" --option local --option cloud
agentos question resolve <question-id> "Local + git sync"

# Re-enter
agentos project show
agentos --json project show     # machine-readable
````

State lives at `~/.agentos/` by default — override with `AGENTOS_HOME` or `--home`.

**Picking a project** (in priority order):

1. `--project <slug>` flag
2. `AGENTOS_PROJECT` env var
3. A `.agentos-project` file (single line: the slug) found by walking up from the current directory — drop one in each repo and `agentos` knows where it is
4. The single existing project, when only one exists

Otherwise `agentos` errors with the list of candidates.

## Layout

```
src/agentos/
  layer1/          # Context/State Layer
    model.py       # Pydantic data models
    codec.py       # Atomic YAML read/write
    store.py       # ContextStore protocol + YamlContextStore
tests/layer1/      # Layer 1 tests
docs/superpowers/specs/  # Design documents
.claude/agents/    # Sub-agent definitions used during development
project.md         # Current architecture state, decisions, open questions
CLAUDE.md          # Working principles for contributors and agents
```

## Development

Requires Python 3.12+ and [`uv`](https://docs.astral.sh/uv/).

```bash
uv run pytest                        # all tests
uv run pytest tests/layer1/ -v       # layer 1 only
uv run pytest -k "test_name"         # single test
```

## Working with this repo

- Read [`project.md`](project.md) at the start of any session for current architecture state.
- Read [`CLAUDE.md`](CLAUDE.md) for working principles.
- Decisions are append-only. Reversals are new entries that supersede the originals.
- Each layer is built only after the one below exposes a stable interface.
