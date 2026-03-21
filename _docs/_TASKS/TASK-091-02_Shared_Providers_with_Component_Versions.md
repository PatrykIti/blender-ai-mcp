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

---

## Acceptance Criteria

- one capability can expose more than one public contract safely
