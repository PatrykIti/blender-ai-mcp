# TASK-114-05-01: Prioritized Existing Tool Fix Register

**Parent:** [TASK-114-05](./TASK-114-05_Prioritized_Fix_Backlog_And_Code_Wave_Plan.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High

**Completion Summary:** The first prioritized fix register is now explicit. The next code/doc wave should start with high-signal wording and semantics cleanup before adding more capability families.

---

## Objective

Produce the prioritized register of existing tools that need wording/behavior fixes first.

---

## Expected Output Shape

- `P0`: severe product confusion / wrong surface semantics
- `P1`: strong wording drift / verification gaps
- `P2`: cleanup and consistency fixes

Each item should state:

- tool/capability
- drift type
- affected files
- fix kind:
  - wording only
  - metadata/doc rewrite
  - behavior fix
  - surface exposure change

---

## Acceptance Criteria

- existing tool cleanup becomes a concrete wave instead of a vague follow-up

## Prioritized Register

### P0

1. Public “mega tools / LLM context optimization” framing  
   Drift type: wording / product semantics  
   Affected files:
   - `README.md`
   - `_docs/_MCP_SERVER/README.md`
   - `_docs/AVAILABLE_TOOLS_SUMMARY.md`
   Fix kind:
   - wording only
   - user-facing doc rewrite

2. `modeling_add_modifier` / modeling wording cluster  
   Drift type: MCP docstring semantics  
   Affected files:
   - `server/adapters/mcp/areas/modeling.py`
   - metadata/docs references that still treat it through old “preferred method / ALT TO” framing
   Fix kind:
   - wording only
   - metadata/doc rewrite

3. `router_*` wording cluster  
   Drift type: product semantics  
   Affected files:
   - `server/adapters/mcp/areas/router.py`
   - user-facing/router docs as needed
   Fix kind:
   - wording only

### P1

4. inventory/internal comments about old mega-tool framing  
   Drift type: implementation/product wording mix  
   Affected files:
   - `server/adapters/mcp/areas/scene.py`
   - `server/adapters/mcp/areas/mesh.py`
   Fix kind:
   - wording cleanup

5. metadata related-tools/examples in modeling/mesh/extraction  
   Drift type: metadata drift  
   Affected files:
   - `server/router/infrastructure/tools_metadata/modeling/**`
   - `server/router/infrastructure/tools_metadata/mesh/**`
   - `server/router/infrastructure/tools_metadata/extraction/**`
   Fix kind:
   - metadata/doc rewrite

6. prompt/demo defaults that still over-normalize manual flows  
   Drift type: prompt/example bias  
   Affected files:
   - `_docs/_PROMPTS/*`
   Fix kind:
   - prompt wording/example rewrite

### P2

7. implementation-level internal comments that still reference the older product rationale  
   Drift type: comment cleanup  
   Affected files:
   - `server/adapters/mcp/areas/*.py`
   Fix kind:
   - cleanup / consistency
