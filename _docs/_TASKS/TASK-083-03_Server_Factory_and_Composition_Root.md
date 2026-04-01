# TASK-083-03: Server Factory and Composition Root

**Parent:** [TASK-083](./TASK-083_FastMCP_3x_Platform_Migration.md)  
**Status:** ✅ Done  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)

---

## Objective

Replace the singleton `mcp = FastMCP("blender-ai-mcp")` model with an explicit composition root that builds a server from reusable provider groups, transforms, and runtime configuration.

## Current State

The composition root is implemented in code: server startup uses `build_server(surface_profile=...)`, surface profiles are explicit, and the platform manifest scaffold is wired into the factory/bootstrap path.

This task is now closed. The composition root is the runtime source of truth, the related tests/docs slice is complete, and the legacy `instance.py` shim has been removed.

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
- `server/adapters/mcp/platform/capability_manifest.py`
- `tests/unit/adapters/mcp/test_server_factory.py`

### Surface Profile Baseline

The composition root should treat these as surface profiles, not versions:

- `legacy-flat`
- `llm-guided`
- `internal-debug`
- `code-mode-pilot`

### Manifest Scaffold Rule

This task establishes the minimal platform-owned manifest scaffold required by the factory/bootstrap baseline.

At this stage the manifest should:

- exist outside router metadata
- be loadable by the composition root
- carry stable capability identifiers and room for later public metadata

It does not need to complete discovery taxonomy, aliases, or full audience/phase tagging yet.
Those are expanded in TASK-084 and TASK-086 on top of this scaffold.

### YAGNI Rule

The first factory implementation should compose from:

- built-in `LocalProvider` instances
- registration functions extracted from current area modules
- built-in FastMCP transforms

Do not block this task on a full redesign of adapter packages or on custom provider abstractions.

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

## Atomic Work Items

1. Replace singleton bootstrap with `build_server(surface_profile=...)`.
2. Define the initial profile matrix and default `LocalProvider` sets.
3. Move startup configuration into one settings object.
4. Introduce the minimal platform manifest scaffold so later discovery and public-surface work extend one shared source of truth.
5. Remove any transitional `instance.py` shim once all areas stop depending on the global singleton.
6. Add profile bootstrap tests before adding any new transform behavior.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-083-03-01](./TASK-083-03-01_Core_Factory_Composition_Root.md) | Core Server Factory and Composition Root | Core implementation layer |
| [TASK-083-03-02](./TASK-083-03-02_Tests_Factory_Composition_Root.md) | Tests and Docs Server Factory and Composition Root | Tests, docs, and QA |

---

## Acceptance Criteria

- `server/main.py` uses an explicit composition root
- more than one server surface can be built from the same runtime
- `instance.py` is no longer the central runtime composition primitive
- the first factory path does not require a repo-specific provider framework beyond reusable `LocalProvider` groups / registrars
- the composition root owns a minimal platform manifest scaffold outside router metadata for later discovery and public-contract work
