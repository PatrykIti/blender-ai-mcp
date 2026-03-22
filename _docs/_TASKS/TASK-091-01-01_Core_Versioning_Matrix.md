# TASK-091-01-01: Core Versioning Policy and Surface Matrix

**Parent:** [TASK-091-01](./TASK-091-01_Versioning_Policy_and_Surface_Matrix.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-03](./TASK-083-03_Server_Factory_and_Composition_Root.md), [TASK-086-01](./TASK-086-01_Public_Surface_Manifest_and_Naming_Conventions.md), [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md)

---

## Objective

Implement the core code changes for **Versioning Policy and Surface Matrix**.

---

## Repository Touchpoints

- `server/adapters/mcp/version_policy.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/platform/public_contracts.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/settings.py`
- `tests/unit/adapters/mcp/test_version_policy.py`

---

## Planned Work

- create `server/adapters/mcp/version_policy.py`
- define surfaces such as:
  - `legacy-flat`
  - `llm-guided`
  - `internal-debug`

### Distinction Rule

This task must define two matrices:

- surface profile matrix
- contract version matrix

Example:

- profile `legacy-flat` may prefer contract line `legacy-v1`
- profile `llm-guided` may prefer contract line `llm-v2`
---

## Acceptance Criteria

- every public surface change has an explicit versioning policy
---

## Atomic Work Items

1. Define one explicit matrix mapping surface profiles to preferred contract lines and deprecation policy.
2. Convert current public contracts into explicit baseline `1.x` lines only after public naming and renderer rules are frozen.
3. Keep version policy owned by the platform layer rather than scattered across area modules or router metadata.
