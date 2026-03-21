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
- `server/adapters/mcp/transforms/versioning.py`
- `tests/unit/adapters/mcp/test_transform_pipeline.py`

### Existing Files To Update

- `server/adapters/mcp/factory.py`
  - build and attach a deterministic transform chain
- `server/adapters/mcp/surfaces.py`
  - define which transforms each surface uses

---

## Baseline Order

1. tagging or metadata enrichment
2. naming or aliasing
3. visibility filtering
4. search transform
5. prompts-as-tools transform
6. version filter

Search should run on already named and filtered components, not the other way around.

---

## Pseudocode

```python
def build_surface_transforms(surface_config, server, providers):
    transforms = []
    transforms.append(TaggingTransform(surface_config.tags))
    transforms.append(NamingTransform(surface_config.naming_rules))
    transforms.append(VisibilityTransform(surface_config.visibility_policy))

    if surface_config.search_enabled:
        transforms.append(SearchTransform(always_visible=surface_config.pinned_tools))

    if surface_config.prompts_as_tools:
        transforms.append(PromptsAsTools(surface_config.prompt_provider))

    if surface_config.version_filter:
        transforms.append(surface_config.version_filter)

    return transforms
```

---

## Tests

- transform order snapshot test
- visibility-before-search test
- naming-before-version-filter lookup test
- prompt bridge coexistence test

---

## Acceptance Criteria

- the server has one explicit transform pipeline
- later platform tasks extend the pipeline instead of bypassing it with custom wrappers
