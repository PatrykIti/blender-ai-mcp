# TASK-083-03: Server Factory and Composition Root

**Parent:** [TASK-083](./TASK-083_FastMCP_3x_Platform_Migration.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)

---

## Objective

Replace the singleton `mcp = FastMCP("blender-ai-mcp")` model with an explicit composition root that builds a server from providers, transforms, and runtime configuration.

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

### New Files To Create

- `server/adapters/mcp/factory.py`
- `server/adapters/mcp/surfaces.py`
- `server/adapters/mcp/settings.py`
- `tests/unit/adapters/mcp/test_server_factory.py`

---

## Pseudocode

```python
from fastmcp import FastMCP


def build_server(surface_config, di) -> FastMCP:
    providers = build_surface_providers(surface_config, di)
    server = FastMCP(
        surface_config.server_name,
        providers=providers,
        list_page_size=surface_config.list_page_size,
        session_state_store=surface_config.session_state_store,
    )

    for transform in build_surface_transforms(surface_config, server, providers):
        server.add_transform(transform)

    return server
```

---

## Tests

- build default surface
- build alternate surface profile
- assert provider order and transform order
- assert bootstrap no longer depends on importing all `areas` modules globally

---

## Acceptance Criteria

- `server/main.py` uses an explicit composition root
- more than one server surface can be built from the same runtime
- `instance.py` is no longer the central runtime composition primitive
