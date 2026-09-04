# TASK-113-02: Surface Exposure Matrix and Hidden Atomic Layer

**Parent:** [TASK-113](./TASK-113_Tool_Layering_Goal_First_And_Vision_Assertion_Strategy.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** TASK-113-01

**Completion Summary:** The first profile/surface exposure matrix is now documented, and the hidden atomic layer plus public escape-hatch rules are explicitly defined in the canonical policy and MCP docs.

---

## Objective

Define which classes of tools should be visible on which surfaces, and make hidden atomic tools a deliberate platform rule instead of an accidental side effect.

---

## Repository Touchpoints

- `_docs/_MCP_SERVER/README.md`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`
- `_docs/_PROMPTS/README.md`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/transforms/visibility_policy.py`
- `server/adapters/mcp/platform/capability_manifest.py`

---

## Planned Work

- define the public exposure matrix by surface/profile
- define which tool classes are:
  - public-default
  - discoverable-on-demand
  - hidden/internal
- define how search/discovery should treat hidden atomic tools
- define the small number of allowed “escape hatch” atomics that can stay public

---

## Acceptance Criteria

- every production-oriented surface has an explicit exposure philosophy
- flat public exposure is no longer the default design assumption
- hidden atomic tools are part of the documented platform model
