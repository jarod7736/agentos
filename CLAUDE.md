# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**AgentOS** — an agent operating system that solves context switching. The core insight: humans and agents share the same problem — both start cold after a session boundary without persistent, structured project state. AgentOS provides that state as a first-class platform capability.

Built layer by layer, bottom-up. Each layer exposes a stable interface before the next is added. Never introduce cross-layer dependencies prematurely.

Always read `project.md` at the start of a session for current architecture state, decisions, and open questions. Use `/project` after any significant design conversation to keep it current.

## Architecture

### Layer 1 — Context/State Layer _(current focus)_
Owns persistent project state: current status, decision history, active focus, open questions. Exposes a read/write interface consumed by both humans and agents. Must survive session boundaries.

Design questions still open — see `project.md` → Open Questions before making implementation decisions.

## Working Principles

**Think Before Coding**
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
uv run pytest -k "test_name"         # single test
```
