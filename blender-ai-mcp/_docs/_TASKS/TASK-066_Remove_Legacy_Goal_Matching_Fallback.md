# TASK-066: Remove Legacy Goal Matching Fallback (Ensemble-Only)

**Status**: ✅ Done  
**Priority**: 🔴 High  
**Category**: Router / UX / Reliability  
**Completed**: 2025-12-17

## Objective

Make Router goal matching **fail-fast** and **explicitly error** when the ensemble matcher is unavailable, instead of silently falling back to legacy matching.

## Motivation

Silent fallback is harmful in production UX:
- Users lose time prompt-tuning against degraded behavior
- Bugs/regressions are hidden (harder to report + debug)
- “It kinda worked” is worse than a clear error for a routing layer

For MCP server behavior, prefer:
1) **Correct + explainable** behavior, or  
2) **Explicit error** with a reason and a clear escalation path (GitHub issue/logs)

## Deliverables

### 1) Remove legacy fallback from goal matching
- `SupervisorRouter.set_current_goal()` must not call `_set_goal_legacy()`.
- If `RouterConfig.use_ensemble_matching` is `False` → raise.
- If ensemble initialization fails → raise with the captured init error.

### 2) Surface errors via `router_set_goal`
- `RouterToolHandler.set_goal()` must catch exceptions from `set_current_goal()` and return:
  - `status: "error"`
  - `error: {type, details, stage}`
  - human-readable `message`

### 3) Update user-facing docs/prompts
- Mention the new `status: "error"` possibility in router-related docs and workflow-first prompt.

### 4) Add/adjust tests
- Unit test: `set_current_goal()` raises on ensemble init failure.
- Unit test: `RouterToolHandler.set_goal()` returns `status="error"` when router raises.

## Implementation Completed

### Files Modified

| File | Change |
|------|--------|
| `server/router/application/router.py` | Removed `_set_goal_legacy()` and made `set_current_goal()` ensemble-only + fail-fast |
| `server/application/tool_handlers/router_handler.py` | Added `status="error"` response on matching exceptions |
| `server/domain/tools/router.py` | Updated contract docs to include `status="error"` |
| `server/adapters/mcp/areas/router.py` | Updated MCP tool docstring to include `status="error"` |
| `_docs/_MCP_SERVER/README.md` | Updated Router tool description (statuses) |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Updated Router tool description (statuses) |
| `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md` | Added handling guidance for `status=="error"` |
| `_docs/_ROUTER/README.md` | Updated router_set_goal status list |
| `tests/unit/router/application/test_supervisor_router.py` | Added regression test for fail-fast init failure |
| `tests/unit/router/application/test_router_handler_parameters.py` | Added handler test for `status="error"` |

## Acceptance Criteria

- [x] No code path falls back to legacy goal matching from `set_current_goal()`.
- [x] `router_set_goal` can return `status: "error"` with actionable reason.
- [x] Docs/prompts mention and handle `status=="error"`.
- [x] Unit tests cover both router raise + handler error response.

## Related

- TASK-053: Ensemble Matcher System
- TASK-055-FIX: Unified Parameter Resolution (`router_set_goal`)
