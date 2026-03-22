# TASK-083-04-01: Core Transform Pipeline Baseline

**Parent:** [TASK-083-04](./TASK-083-04_Transform_Pipeline_Baseline.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-03](./TASK-083-03_Server_Factory_and_Composition_Root.md)

---

## Objective

Implement the core code changes for **Transform Pipeline Baseline**.

---

## Repository Touchpoints

- `server/adapters/mcp/server.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/context_utils.py`
- `server/adapters/mcp/dispatcher.py`

---

## Planned Work

### New Files To Create

- `server/adapters/mcp/transforms/__init__.py`
- `server/adapters/mcp/transforms/naming.py`
- `server/adapters/mcp/transforms/visibility.py`
- `server/adapters/mcp/transforms/discovery.py`
- `server/adapters/mcp/transforms/prompts_bridge.py`
- `tests/unit/adapters/mcp/test_transform_pipeline.py`

### Existing Files To Update

- `server/adapters/mcp/factory.py`
  - build and attach a deterministic transform chain
- `server/adapters/mcp/surfaces.py`
  - define which transforms each surface uses
---

## Acceptance Criteria

- the server has one explicit transform pipeline
- later platform tasks extend the pipeline instead of bypassing it with custom wrappers
---

## Atomic Work Items

1. Prove the final transform order against FastMCP 3.x semantics before coding custom wrappers.
2. Use built-in `ToolTransform`, `Visibility`, `PromptsAsTools`, `BM25SearchTransform`, and `VersionFilter` wherever they fit.
3. Keep custom repo-specific code focused on configuration and manifest translation.
4. Add one snapshot-style transform-order test per surface profile.
