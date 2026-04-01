# 161 - 2026-03-29: Guided goal recovery and reference semantics

**Status**: ✅ Completed  
**Type**: Guided UX / Router / Reference Flow  
**Task**: TASK-121-06

---

## Summary

Closed four remaining guided-session semantic gaps that showed up in real
reference-driven modeling flows:

- reference-guided low-poly squirrel goals no longer default into irrelevant
  workflow families
- `reference_images(...)` can now stage pending attachments before the active
  goal exists
- public `scene_*` helper tools no longer execute unrelated pending workflows
- weak workflow confirmation can now explicitly decline into
  `guided_manual_build`

---

## Changes

- Added a reference-guided manual-build boundary in `router_set_goal(...)` for
  low-poly squirrel/animal-style goals with front/side references.
- Added pending reference-image staging and automatic adoption on the next goal
  set.
- Bypassed router workflow triggering for direct user calls to public
  `scene_*` tools.
- Extended model-facing `workflow_confirmation` so `guided_manual_build` can be
  used as an explicit rejection path.
- Updated public MCP docs, prompt docs, task docs, and tool inventory to
  explain the new semantics.

---

## Validation

- `poetry run pytest -q tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/adapters/mcp/test_session_phase.py tests/unit/router/application/test_router_handler_parameters.py tests/e2e/router/test_guided_manual_handoff.py`
- `poetry run ruff check server/adapters/mcp/router_helper.py server/adapters/mcp/session_capabilities.py server/adapters/mcp/areas/reference.py server/application/tool_handlers/router_handler.py tests/unit/adapters/mcp/test_reference_images.py tests/unit/adapters/mcp/test_context_bridge.py tests/unit/router/application/test_router_handler_parameters.py tests/e2e/router/test_guided_manual_handoff.py`
