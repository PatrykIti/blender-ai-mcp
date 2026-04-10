# TASK-130-01-01: Align Runtime Default Client Examples And Operator Story

**Parent:** [TASK-130-01](./TASK-130-01_Default_Guided_Bootstrap_And_Request_Triage_Consistency.md)
**Status:** ⏳ To Do
**Priority:** 🔴 High

## Objective

Close the remaining bootstrap/docs/client-example drift so operators and MCP
clients all start from the same guided production story.

## Repository Touchpoints

- `server/infrastructure/config.py`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/_MCP_SERVER/MCP_CLIENT_CONFIG_EXAMPLES.md`

## Planned Code/Doc Shape

```text
Production default:
- which surface boots by default
- what request types the model should classify first
- what the canonical recovery/inspection tools are
```

## Acceptance Criteria

- config defaults, README, MCP docs, and client examples agree on the guided
  production posture

## Tests To Add/Update

- `tests/unit/infrastructure/test_env_example.py`
- `tests/unit/adapters/mcp/test_public_surface_docs.py`

## Changelog Impact

- include in the parent TASK-130 changelog entry
