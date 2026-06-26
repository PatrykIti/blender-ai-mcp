# TASK-189: Public docs/ Directory Split And Migration

**Follow-on After:** [TASK-188](./TASK-188_AGENTS_Governance_Rules_Merge.md)
**Status:** ⏳ To Do
**Priority:** 🟡 Medium
**Category:** Repo Governance / Documentation
**Created:** 2026-06-26

## Objective

Create the public `docs/` directory and migrate the user/operator-facing
documentation currently living under `_docs/` into it, following the `docs/` vs
`_docs/` split codified in `AGENTS.md` by TASK-188. `_docs/` stays the internal,
technical, agent/LLM-facing surface.

## Background

TASK-188 added the split rule but deliberately did not create `docs/` or move any
files, because migration churns the ~30 `_docs/` cross-references in `AGENTS.md`
plus the `README.md` "Documentation Map", and that link maintenance warrants its
own scoped task.

## Scope

Promote, in priority order, the user-facing docs identified during the TASK-188
understanding pass:

1. `_docs/_PROMPTS/` -> `docs/` (copy/paste prompt & usage guide for end users).
2. `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` -> `docs/` (MCP client setup).
3. `_docs/_ROUTER/QUICK_START.md` -> `docs/` (getting-started walkthrough).
4. `_docs/_ROUTER/WORKFLOWS/*tutorial*` / `*guide*` -> evaluate a user-authoring
   vs internal-engine-semantics split before moving.

## Non-Goals

- Moving internal design/contract/task/changelog docs out of `_docs/`.
- Rewriting the content of the promoted docs beyond link/path fixes.

## Repository Touchpoints

| Path | Expected Ownership | Why In Scope |
|------|--------------------|--------------|
| `docs/` (new) | Docs | Public/user-facing documentation root |
| `_docs/_PROMPTS/` | Docs | Top migration candidate |
| `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md` | Docs | Client-setup migration candidate |
| `_docs/_ROUTER/QUICK_START.md` | Docs | Getting-started migration candidate |
| `_docs/_ROUTER/WORKFLOWS/` | Docs | Mixed user/internal — split decision |
| `AGENTS.md` | Governance | Update `_docs/` cross-references for moved docs |
| `README.md` | Docs | Update the "Documentation Map" links |

## Acceptance Criteria

- `docs/` exists and contains the promoted user-facing docs.
- No moved doc leaves a dangling link; `AGENTS.md` and `README.md` point at the
  new locations.
- `_docs/` retains only internal/technical/agent-facing material.
- A `_docs/_CHANGELOG/*` entry records the migration and the index is updated.

## Tests / Validation

- `git diff --check`.
- Link-consistency grep: no surviving references to the old paths of moved docs.
- `poetry run pre-commit run --files <moved + edited files>`.

## Docs To Update

- `AGENTS.md`, `README.md` (Documentation Map), `_docs/_CHANGELOG/`, and
  `_docs/_TASKS/README.md`.

## Changelog Impact

One `_docs/_CHANGELOG/*` entry referencing TASK-189 when the migration ships.
