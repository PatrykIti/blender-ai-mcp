# TASK-118-04-01: Metadata and Public Surface Delivery

**Parent:** [TASK-118-04](./TASK-118-04_Metadata_Docs_And_Roundtrip_Coverage.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium

**Completion Summary:** `scene_configure` is now represented in router metadata, public inventories, MCP docs, addon docs, and task/status docs so the inspect/configure split is explicit across the repo.

---

## Objective

Keep metadata, public docs, and grouped-tool inventories aligned with the new
scene configuration surface.

---

## Exact Targets

- `server/router/infrastructure/tools_metadata/scene/`
- `README.md`
- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_ADDON/README.md`

---

## Acceptance Criteria

- new scene tools are described through the grouped public surface model
- public docs make the inspect/configure split explicit
