# TASK-099-02-01-01: Runtime Version Guards and Error Surfaces

**Parent:** [TASK-099-02-01](./TASK-099-02-01_Core_Runtime_Guards_and_Containment.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-099-01](./TASK-099-01_Compatibility_Matrix_and_Reproduction_Harness.md)

---

## Objective

Fail fast when the repo is started on an unsupported FastMCP+Docket task-runtime pair.

---

## Repository Touchpoints

- `server/adapters/mcp/factory.py`
- `server/main.py`
- `server/infrastructure/config.py`

---

## Planned Work

- detect unsupported task-runtime combinations
- expose clear error messages for startup or task registration failures

### Error Surface Detail

- server bootstrap path
- task registration path
- task submission path

Messages should name both resolved versions and the supported policy, not only raise a generic runtime error.

---

## Acceptance Criteria

- unsupported runtime combinations are visible as explicit platform errors
