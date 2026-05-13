# /project — Update project context

Read `project.md` in the repo root. Then, based on everything in the current conversation (decisions made, layers defined, architecture discussed, tools chosen, constraints identified), update the file to reflect the current state of the project.

Rules:
- Append new context; do not erase prior decisions unless they were explicitly reversed.
- Keep each section tight — one decision or fact per bullet, no prose padding.
- After writing, confirm what sections changed and why.

If `project.md` does not exist yet, create it with the structure below.

## project.md structure

```markdown
# AgentOS — Project Context

## Purpose
One-paragraph description of what AgentOS is and what problem it solves.

## Layered Architecture
Ordered list of layers, bottom-up. For each layer: name, responsibility, and key interface it exposes to the layer above.

## Technology Decisions
Bullets: decision → rationale. Only firm decisions, not candidates.

## Constraints & Non-Goals
Bullets: things explicitly ruled out or deferred.

## Open Questions
Bullets: unresolved design questions with any known options.
```
