# 110 - 2025-12-14: Picnic Table Supports + Enum/Computed Param Robustness

**Status**: ✅ Completed  
**Type**: Bug Fix / Workflow / Testing  
**Task**: Follow-up to [TASK-055](../_TASKS/TASK-055_Interactive_Parameter_Resolution.md), [TASK-056](../_TASKS/TASK-056_Workflow_System_Enhancements.md)

---

## Summary

Improved the picnic table workflow so benches are properly supported (no floating geometry), and strengthened Router parameter validation around `enum` and computed parameters to prevent invalid inputs and learned-value drift.

---

## Changes

### Picnic table workflow: bench supports + crossbeams

- Bench support beams are aligned to the bench underside for `bench_layout != "none"`.
- Crossbeams/diagonal supports now span benches correctly for `"sides"` and `"all"` layouts.
- Support/crossbeam creation runs when benches exist, even if `include_a_frame_supports` is `false`.

### Router tool UX: enum-aware unresolved + value normalization

- `router_set_goal` now includes `enum` options in `unresolved` responses (so the caller/LLM can pick valid values).
- Enum values are normalized (trimmed, case-insensitive, quotes handled).
- Invalid enum values return `status: "needs_input"` with an error instead of being silently accepted/ignored.

### Computed parameters: treated as internal outputs

- Computed params are no longer:
  - requested as interactive `unresolved` inputs,
  - resolved from learned mappings,
  - stored back into learned memory.
- Explicit overrides via `resolved_params` are still supported.

---

## Files Modified (high level)

- Workflow:
  - `server/router/application/workflows/custom/picnic_table.yaml`
- Runtime:
  - `server/application/tool_handlers/router_handler.py`
  - `server/router/application/resolver/parameter_resolver.py`
- Tests:
  - `tests/unit/application/test_router_handler_parameters.py`
  - `tests/unit/router/application/resolver/test_parameter_resolver.py`
- Docs:
  - `_docs/_ROUTER/WORKFLOWS/yaml-workflow-guide.md`
  - `_docs/_ROUTER/WORKFLOWS/creating-workflows-tutorial.md`

---

## Validation

```bash
poetry run pytest -q
```
