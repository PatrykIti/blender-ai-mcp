# TASK-091-02: Shared Providers with Component Versions

**Parent:** [TASK-091](./TASK-091_Versioned_Client_Surfaces.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-091-01](./TASK-091-01_Versioning_Policy_and_Surface_Matrix.md)

---

## Objective

Attach versions to shared provider components so more than one public contract can coexist without duplicating handler implementations.

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

1. Assign baseline versions to the legacy public contracts.
2. Add alternate versions only for the capabilities that actually need public evolution.
3. Add tests proving shared provider components can expose multiple versions without duplicating handler code.
