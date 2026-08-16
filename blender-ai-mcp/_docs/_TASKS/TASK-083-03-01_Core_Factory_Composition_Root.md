# TASK-083-03-01: Core Server Factory and Composition Root

**Parent:** [TASK-083-03](./TASK-083-03_Server_Factory_and_Composition_Root.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)  

---

## Objective

Implement the core code changes for **Server Factory and Composition Root**.

---

## Repository Touchpoints

- `server/adapters/mcp/instance.py`
- `server/adapters/mcp/server.py`
- `server/main.py`
- `server/infrastructure/config.py`
- `server/infrastructure/di.py`

---

## Planned Work

### Existing Files To Update

- `server/adapters/mcp/instance.py`
  - reduce it to a compatibility shim or remove its role as the runtime source of truth
- `server/adapters/mcp/server.py`
  - expose `build_server()` and `run_server(surface=...)`
- `server/main.py`
  - bootstrap through a factory instead of import side effects
- `server/infrastructure/config.py`
  - add surface-profile and server-factory options
  - keep profile selection distinct from later contract-version filtering

### New Files To Create

- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/settings.py`
- `tests/unit/adapters/mcp/test_server_factory.py`

### Surface Profile Baseline

The composition root should treat these as surface profiles, not versions:

- `legacy-flat`
- `llm-guided`
- `internal-debug`
- `code-mode-pilot`
---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-083-03-01-01](./TASK-083-03-01-01_Surface_Profile_Settings_and_Config.md) | Surface Profile Settings and Config | Core slice |
| [TASK-083-03-01-02](./TASK-083-03-01-02_Server_Factory_and_Bootstrap_Path.md) | Server Factory and Bootstrap Path | Core slice |

---

## Acceptance Criteria

- `server/main.py` uses an explicit composition root
- more than one server surface can be built from the same runtime
- `instance.py` is no longer the central runtime composition primitive
---

## Atomic Work Items

1. Introduce one explicit factory path that builds a server from providers, transforms, and settings.
2. Keep `instance.py` as a compatibility shim only while area modules still import it.
3. Prove the bootstrap path works before broad provider migration continues.
