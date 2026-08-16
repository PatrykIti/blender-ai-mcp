# 261. Guided role-group validation

Date: 2026-04-26

## Summary

Closed a guided-governor bypass where caller-controlled `role_group` values
could reclassify role-sensitive mutating tools before family enforcement.

## What Changed

- in `server/adapters/mcp/session_capabilities.py`:
  - validate optional `role_group` values against the domain role map
  - reject mismatches such as `guided_role="body_core"` with
    `role_group="utility"` instead of storing the supplied group
- in `server/adapters/mcp/router_helper.py`:
  - added an explicit guided role-group policy check before the utility-family
    fast path
  - derive enforcement from the validated role mapping so role-sensitive
    mutators cannot bypass phase gates by supplying a different group
- in focused unit tests:
  - covered the direct `modeling_create_primitive(...)` bypass attempt during a
    spatial-context gate
  - covered guided part-role registration rejecting mismatched role groups

## Documentation

- updated `README.md` guided role-hint notes
- updated `_docs/_MCP_SERVER/README.md` guided execution policy notes

## Validation

- `PYTHONPATH=. poetry run pytest tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py -q -k "mismatched_role_group or fail_closes_when_guided_family_is_not_allowed or strips_guided_policy_params"`
  - result on this machine: `4 passed`
- `PYTHONPATH=. poetry run pytest tests/unit -q`
  - result on this machine: `3097 passed`
- `poetry run ruff check server/adapters/mcp/router_helper.py server/adapters/mcp/session_capabilities.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - result on this machine: passed
- `poetry run mypy server/adapters/mcp/router_helper.py server/adapters/mcp/session_capabilities.py`
  - result on this machine: passed
- `PRE_COMMIT_HOME=/tmp/pre-commit-cache poetry run pre-commit run --files README.md _docs/_MCP_SERVER/README.md _docs/_CHANGELOG/README.md _docs/_CHANGELOG/261-2026-04-26-guided-role-group-validation.md server/adapters/mcp/router_helper.py server/adapters/mcp/session_capabilities.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_guided_flow_state_contract.py`
  - result on this machine: passed
