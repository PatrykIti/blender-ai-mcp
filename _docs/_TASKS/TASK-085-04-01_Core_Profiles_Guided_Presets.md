# TASK-085-04-01: Core Client Profiles and Guided Mode Presets

**Parent:** [TASK-085-04](./TASK-085-04_Client_Profiles_and_Guided_Mode_Presets.md)  
**Status:** ✅ Done  
**Priority:** 🟡 Medium  
**Depends On:** [TASK-085-02](./TASK-085-02_Visibility_Policy_Engine_and_Tagged_Providers.md)

---

## Objective

Implement the core code changes for **Client Profiles and Guided Mode Presets**.

---

## Repository Touchpoints

- `server/adapters/mcp/client_profiles.py`
- `server/adapters/mcp/guided_mode.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/settings.py`
- `tests/unit/adapters/mcp/test_client_profiles.py`
---

## Planned Work

- create:
  - `server/adapters/mcp/client_profiles.py`
  - `server/adapters/mcp/guided_mode.py`
  - `tests/unit/adapters/mcp/test_client_profiles.py`
- support profiles such as:
  - `legacy-flat`
  - `llm-guided`
  - `internal-debug`
  - `code-mode-pilot`
---

## Acceptance Criteria

- surface profiles can be selected without forking tool handler logic
- guided mode hides low-level noise while preserving deeper access through search or alternate profiles
---

## Atomic Work Items

1. Align profile names with the server factory and versioning matrix.
2. Define exactly which providers and transforms each profile uses.
3. Add one golden test per profile for visible entry tools.