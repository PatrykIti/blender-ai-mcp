# TASK-083-04: Transform Pipeline Baseline

**Parent:** [TASK-083](./TASK-083_FastMCP_3x_Platform_Migration.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-03](./TASK-083-03_Server_Factory_and_Composition_Root.md)

---

## Objective

Introduce a base transform pipeline that becomes the canonical place for naming, visibility, discovery, prompt bridging, and versioning concerns.

---

## Repository Touchpoints

- `server/adapters/mcp/server.py`
- `server/adapters/mcp/router_helper.py`
- `server/adapters/mcp/context_utils.py`
- `server/adapters/mcp/dispatcher.py`
- `_docs/_ROUTER/RESPONSIBILITY_BOUNDARIES.md`

---

## Planned Work

### New Files To Create

- `server/adapters/mcp/transforms/__init__.py`
- `server/adapters/mcp/transforms/naming.py`
- `server/adapters/mcp/transforms/visibility.py`
- `server/adapters/mcp/transforms/discovery.py`
- `server/adapters/mcp/transforms/prompts_bridge.py`
- `tests/unit/adapters/mcp/test_transform_pipeline.py`

### Existing Files To Update

- `server/adapters/mcp/factory.py`
  - build and attach a deterministic transform chain
- `server/adapters/mcp/surfaces.py`
  - define which transforms each surface uses

---

## Baseline Order

1. provider composition
2. built-in `VersionFilter` application
3. tool and argument reshaping
4. prompts-as-tools or resources-as-tools bridge when the surface needs it
5. static visibility filtering
6. search or Code Mode transform

Search should run on the already versioned and already reshaped public surface.
If prompt bridge tools should be discoverable, they must exist before search is applied.

---

## Pseudocode

```python
def build_surface_transforms(surface_config, server, providers):
    transforms = []
    if surface_config.version_filter:
        transforms.append(surface_config.version_filter)

    transforms.append(NamingTransform(surface_config.naming_rules))

    if surface_config.prompts_as_tools:
        transforms.append(PromptsAsTools(surface_config.prompt_provider))

    transforms.append(VisibilityTransform(surface_config.visibility_policy))

    if surface_config.search_enabled:
        transforms.append(SearchTransform(always_visible=surface_config.pinned_tools))

    return transforms
```

---

## Tests

- transform order snapshot test
- visibility-before-search test
- version-before-naming lookup test
- prompt bridge coexistence test

---

## Atomic Work Items

1. Prove the final transform order against FastMCP 3.x semantics before coding custom wrappers.
2. Use built-in `ToolTransform`, `Visibility`, `PromptsAsTools`, `BM25SearchTransform`, and `VersionFilter` wherever they fit.
3. Keep custom repo-specific code focused on configuration and manifest translation.
4. Add one snapshot-style transform-order test per surface profile.

---

## Acceptance Criteria

- the server has one explicit transform pipeline
- later platform tasks extend the pipeline instead of bypassing it with custom wrappers
