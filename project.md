# AgentOS — Project Context

## Purpose
AgentOS is an agent operating system built layer by layer. It solves the problem of context switching — the expensive cognitive re-load required when returning to a project after a context boundary (session end, task switch, etc.). This problem is identical for humans and agents: both start cold without persistent, structured project state. AgentOS provides that state as a first-class platform capability, making re-entry instant rather than expensive.

## Layered Architecture
Bottom-up build order. Each layer must be stable before the next is added.

1. **Context/State Layer** _(Layer 1 — current focus)_
   - Responsibility: owns persistent project state — current status, decision history, active focus, open questions
   - Interface: read/write API consumed by both humans and agents
   - Goal: survive session boundaries; make project context instantly retrievable

2. **Integration Layer** _(Layer 2 — planned)_
   - Responsibility: bidirectional sync with external systems
   - Primary integration: 2nd Brain Obsidian vault (git@github.com:jarod7736/2ndBrain.git)
     - **Write path**: `gh api repos/jarod7736/2ndBrain/contents/raw/notes/<slug>.md` (PUT) with base64-encoded content + commit message → `brain-ingest` processes into wiki pages
     - **Read path**: `gh api repos/jarod7736/2ndBrain/contents/<path>` (GET) + base64 decode — reads `index.md` then relevant `wiki/` pages
     - Both paths use authenticated `gh` CLI (no GitHub MCP server required)
     - Vault also has `brain-lint` for content quality validation
   - 2nd Brain ingests files/links/data and stores them in wiki format under `wiki/` (master index at `index.md`)
   - Interface: pluggable adapters per external system; Layer 1 has no knowledge of Layer 2

## Technology Decisions
- **Runtime**: Python 3.12+
- **Build/packaging**: `uv` + `pyproject.toml`
- **Storage (Layer 1)**: Structured YAML files (`~/.agentos/projects/`)
- **Project boundary**: Named entity (user-defined slug) with Goals nested within
- **Decision log**: append-only — decisions are never overwritten or deleted

## Constraints & Non-Goals
- Layers are built sequentially; no layer depends on one above it.
- Each layer exposes a stable interface before construction of the next begins.
- Layer 1 has zero knowledge of external systems — integration is Layer 2's concern.
- AgentOS does not duplicate knowledge that can be read from 2nd Brain.

## Open Questions
- Deployment model (local, cloud, hybrid)?
- How does context get populated? (manually, agent-assisted, inferred from git/tickets?)
