# TASK-090-02: FastMCP Prompt Provider and Rendering

**Parent:** [TASK-090](./TASK-090_Prompt_Layer_and_Tool_Compatible_Prompts.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-090-01](./TASK-090-01_Prompt_Asset_Inventory_and_Taxonomy.md)

---

## Objective

Expose prompt assets as native FastMCP prompt components with structured rendering support.

---

## Planned Work

- create:
  - `server/adapters/mcp/prompts/provider.py`
  - `server/adapters/mcp/prompts/rendering.py`
  - `tests/unit/adapters/mcp/test_prompt_provider.py`

---

## Acceptance Criteria

- prompt-capable clients can list and fetch prompt products directly through the server
