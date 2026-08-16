# 227. Guided execution enforcement and role sequencing

Date: 2026-04-09

## Summary

Completed the execution-enforcement continuation of TASK-150 so the guided
runtime now owns not just flow state and visibility shaping, but also
family-aware execution guards, semantic part-role registration, and
role-group-driven step transitions.

## What Changed

- added shared guided tool families and overlay family order
- added internal guided part registry session state
- exposed compact role summaries on `guided_flow_state`:
  - `allowed_roles`
  - `completed_roles`
  - `missing_roles`
  - `required_role_groups`
- added canonical `guided_register_part(...)` for semantic part registration
- added optional `guided_role` hints on `modeling_create_primitive(...)` and
  `modeling_transform_object(...)`
- extended router execution context with guided family/role metadata
- fail-closed guided execution now blocks:
  - wrong family for the current step
  - wrong explicit role for the current step
  - role-sensitive build calls without explicit or previously registered role
- flow progression now advances from role-group completion:
  - `create_primary_masses` -> `place_secondary_parts`
  - `place_secondary_parts` -> `checkpoint_iterate`
- updated README, MCP docs, prompt docs, and the full TASK-150 tree to match
  the shipped model

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_guided_flow_state_contract.py tests/unit/adapters/mcp/test_contract_payload_parity.py tests/unit/adapters/mcp/test_visibility_policy.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_router_elicitation.py tests/unit/adapters/mcp/test_search_surface.py tests/unit/adapters/mcp/test_legacy_flat_pagination_compat.py -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py tests/unit/router/application/test_correction_audit.py -q`
- `PYTHONPATH=. poetry run pytest tests/e2e/integration/test_guided_surface_contract_parity.py::test_guided_surface_contract_parity_over_stdio tests/e2e/integration/test_guided_streamable_spatial_support.py::test_streamable_guided_session_expands_visible_tools_after_goal_handoff -q`
- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_public_surface_docs.py -q`

## Why

Before this wave, TASK-150 could gate bootstrap and spatial-context work, but
once build unlocked the model still had too much freedom inside the broad
build family. This continuation gives the server enough semantic structure to
constrain the order of primary masses vs secondary parts without multiplying
the public MCP surface into one macro tool per domain part.
