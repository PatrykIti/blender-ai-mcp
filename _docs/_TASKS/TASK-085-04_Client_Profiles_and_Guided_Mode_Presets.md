# TASK-085-04: Client Profiles and Guided Mode Presets

**Parent:** [TASK-085](./TASK-085_Session_Adaptive_Tool_Visibility.md)  
**Status:** ⬜ Planned  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-085-02](./TASK-085-02_Visibility_Policy_Engine_and_Tagged_Providers.md)

---

## Objective

Introduce visibility presets for different clients and a guided-mode surface that reduces active action space without removing deeper capabilities from the repo.

---

## Planned Work

- create:
  - `server/adapters/mcp/client_profiles.py`
  - `server/adapters/mcp/guided_mode.py`
  - `tests/unit/adapters/mcp/test_client_profiles.py`
- support profiles such as:
  - `legacy-flat`
  - `llm-first`
  - `guided-router-first`
  - `internal-debug`

---

## Acceptance Criteria

- surface profiles can be selected without forking tool handler logic
- guided mode hides low-level noise while preserving deeper access through search or alternate profiles
