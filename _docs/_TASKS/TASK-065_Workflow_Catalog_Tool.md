# TASK-065: Replace `vector_db_manage` with `workflow_catalog`

## Goal
Remove the MCP tool `vector_db_manage` (vector DB admin tool) and replace it with a read-only workflow exploration tool:

- `workflow_catalog` (list/get/search)
- **Note (2025-12-21):** Import support was added later in TASK-075, including inline and chunked upload paths.
- Must **not** execute workflows
- Must allow inspecting workflow `steps` to help LLM “imagine”/plan modeling

## Motivation
`vector_db_manage` mixed multiple responsibilities (DB stats, migrations, destructive actions) under a name that didn’t match the primary UX need: “show me workflows similar to my goal and let me inspect their steps”.

We want:
- a **safe, read-only** public tool surface for workflow discovery/inspection
- a tool name aligned with what the LLM/user wants to do

## Deliverables

### 1) New Tool: `workflow_catalog`
Add MCP tool:
- `workflow_catalog(action="list")` → list workflows + metadata
- `workflow_catalog(action="get", workflow_name="...")` → return workflow definition incl. `steps`
- `workflow_catalog(action="search", query="...", top_k=..., threshold=...)` → similar workflows (semantic when available; keyword fallback)
  - Later extended with `import` (file/inline/chunked) in TASK-075

Implementation should follow the existing Clean Architecture pattern:
- Domain interface: `server/domain/tools/workflow_catalog.py`
- Handler: `server/application/tool_handlers/workflow_catalog_handler.py`
- DI provider: `server/infrastructure/di.py` (`get_workflow_catalog_handler`)
- MCP area: `server/adapters/mcp/areas/workflow_catalog.py`
- Registration: `server/adapters/mcp/areas/__init__.py`

### 2) Remove Tool: `vector_db_manage`
Remove MCP tool implementation and registration:
- delete `server/adapters/mcp/areas/vector_db.py`
- remove any imports/references from MCP areas

### 3) Documentation Updates
Update user-facing docs to reflect the new tool:
- `_docs/_MCP_SERVER/README.md` (tool table)
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/WORKFLOW_ROUTER_FIRST.md` (replace old “preview matches” step)
- `_docs/_ROUTER/README.md` (components table)
- `_docs/_ROUTER/IMPLEMENTATION/32-lance-vector-store.md` (MCP tool section)
- `README.md` (tool allowlist examples)

## Acceptance Criteria
- `workflow_catalog` is available via MCP and returns JSON (string) results
- No public MCP tool exists that performs destructive vector DB management actions
- No docs/prompts reference `vector_db_manage` as a current tool
- `workflow_catalog` does not call `router_set_goal` (no workflow execution)
