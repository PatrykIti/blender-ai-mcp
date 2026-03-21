# TASK-091-02-01: Core Shared Providers with Component Versions

**Parent:** [TASK-091-02](./TASK-091-02_Shared_Providers_with_Component_Versions.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-091-01](./TASK-091-01_Versioning_Policy_and_Surface_Matrix.md), [TASK-086-01](./TASK-086-01_Public_Surface_Manifest_and_Naming_Conventions.md), [TASK-089-01](./TASK-089-01_Contract_Catalog_and_Response_Guidelines.md)

---

## Objective

Implement the core code changes for **Shared Providers with Component Versions**.

---

## Repository Touchpoints

- `server/adapters/mcp/providers/core_tools.py`
- `server/adapters/mcp/providers/router_tools.py`
- `server/adapters/mcp/providers/workflow_tools.py`
- `server/adapters/mcp/platform/public_contracts.py`
- `server/adapters/mcp/platform/capability_manifest.py`
- `tests/unit/adapters/mcp/test_provider_versions.py`

---

## Planned Work

- version provider-registered tools and prompts where surface evolution requires it
- keep the business layer shared

### Migration Rule

For any public component name that will gain multiple versions:

1. assign an explicit version to the current implementation first
2. add the new implementation under the same public name with a higher version
3. never mix versioned and unversioned forms of the same public name
---

## Acceptance Criteria

- one capability can expose more than one public contract safely
---

## Atomic Work Items

1. Assign explicit baseline versions to the current public contracts on shared providers without duplicating handler implementations.
2. Add alternate versions only for capabilities whose public name, parameter contract, or response contract actually changes.
3. Keep internal canonical tool names and dispatcher mappings unversioned unless the internal execution contract truly changes.
