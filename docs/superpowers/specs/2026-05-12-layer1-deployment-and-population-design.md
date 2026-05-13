# Layer 1 — Deployment Model and Population Path

**Date:** 2026-05-12
**Status:** Approved
**Scope:** Closes the two open questions in `project.md` and locks the Layer 1 ↔ Layer 2 contract.

## Context

Layer 1 (Context/State) is implemented and tested. `project.md` still listed two open questions:

1. Deployment model (local / cloud / hybrid)?
2. How does context get populated (manually / agent-assisted / inferred)?

Both answers shape Layer 2 (Integration Layer). Resolving them now is cheaper than refactoring the adapter contract later.

## Decisions

### D1 — Deployment: local + user-managed git

- One state directory. Default `~/.agentos/`, override via `AGENTOS_HOME` env var or `--home` flag.
- One project = one YAML file at `<home>/projects/<slug>.yaml`. (Already implemented.)
- Git is the user's responsibility, not AgentOS's. AgentOS does not run `git` commands. The user `git init`s the home directory and pushes/pulls when they want cross-device sync.
- Single-user, single-machine. No locking, no daemon. The existing atomic-write codec is sufficient.

**Tradeoff:** No auto-sync. If the user forgets to push, other machines drift. Accepted — matches how `2ndBrain` already works.

### D2 — Population: agent-assisted via CLI; no inference

- Primary write path: agents shell out to an `agentos` CLI at conversation boundaries (decision made, goal completed, focus shifted). Same pattern as `/project` today.
- Humans write via the same CLI. No separate human ceremony.
- One CLI invocation = one append or one update. No batch commands in v1.
- No inference. AgentOS does not scrape git logs, PR descriptions, or chat transcripts. If a decision is not explicitly logged, it does not exist in AgentOS.
- Reads are cheap and frequent (`agentos project show`); writes are deliberate.

**Tradeoff:** Deliberate writes mean state can drift from reality if logging is forgotten. Mitigation: keep `decision add` / `focus set` low-friction so logging is the path of least resistance.

### D3 — Agent surface: CLI now, MCP server later

- `agentos` CLI is a thin wrapper over `agentos.layer1.ContextStore`. No business logic in the CLI.
- An MCP server is a later layer. It will wrap the same `ContextStore`, not the CLI.
- The Python library API stays primary. Embedding consumers (including Layer 2) import `agentos.layer1` directly.

## CLI surface (v1)

Verbs match the data model, not generic CRUD:

| Command | Effect |
| --- | --- |
| `agentos project init <slug>` | Create a new project YAML. |
| `agentos project show [<slug>]` | Print project state. `--format=text\|yaml\|json`. |
| `agentos decision add "<text>"` | Append a decision. Append-only is enforced here. |
| `agentos goal add "<text>"` | Add a goal. |
| `agentos goal complete <id>` | Mark a goal complete. |
| `agentos focus set "<text>"` | Replace current active focus. |
| `agentos question add "<text>"` | Add an open question. |
| `agentos question resolve <id> "<answer>"` | Resolve a question with an answer. |

**Current-project resolution.** Each command takes an optional `--project <slug>`. If omitted: fall back to `AGENTOS_PROJECT` env var, then to the single existing project if only one exists. Error if ambiguous.

**Output contract.** Plain text on success; structured JSON on `--json`. Errors to stderr, non-zero exit. Agents call with `--json`; humans read the default text.

## Layer 1 ↔ Layer 2 contract

The Integration Layer, when it is built, must conform to these rules. They are stated here so Layer 1 changes do not silently break Layer 2 later.

- **L2 reads/writes via `ContextStore`.** Even though the YAML files are human-readable on disk, L2 treats them as opaque. Storage format remains swappable.
- **L2 calls the Python API, not the CLI.** The CLI is for agents shelling out. L2 is Python code; it imports `agentos.layer1`.
- **L2 is git-agnostic.** L2 does not know AgentOS state may be in a git repo. 2nd Brain sync is independent of any `git push` on `~/.agentos/`.
- **Unit of sync is the project.** A 2nd Brain wiki page corresponds to one AgentOS project. Decisions, goals, focus are rendered into the page; they are not separately addressable from L2's perspective.
- **L1 has no knowledge of L2.** No hooks, callbacks, or events. L2 syncs on user trigger or schedule, not on every L1 write.

**Tradeoff:** No event stream from L1 means L2 cannot be "live." Sync happens on user trigger or schedule. Consistent with the deliberate-write model in D2.

## Non-goals (v1)

- Multi-user / multi-machine concurrency.
- Auto-sync (git, cloud, anything).
- Inference from git, tickets, or chat.
- Cross-project queries / global search.
- A daemon or background process.
- An MCP server. (Deferred to a later layer.)

## What this unblocks

- Layer 1 CLI implementation (new work).
- Layer 2 design with a stable, written L1 contract.

## What this does not decide

- The exact `ContextStore` Protocol additions (if any) needed for the new CLI verbs. Implementation plan will surface gaps.
- Layer 2's internal architecture. That is a separate design.
