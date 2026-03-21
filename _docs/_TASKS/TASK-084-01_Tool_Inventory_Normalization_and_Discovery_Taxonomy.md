# TASK-084-01: Tool Inventory Normalization and Discovery Taxonomy

**Parent:** [TASK-084](./TASK-084_Dynamic_Tool_Discovery.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)

---

## Objective

Create one canonical discovery inventory containing categories, tags, aliases, and visibility flags for every MCP-facing capability.

---

## Repository Touchpoints

- `server/router/infrastructure/metadata_loader.py`
- `server/router/infrastructure/tools_metadata/**`
- `server/adapters/mcp/areas/*.py`
- `server/adapters/mcp/dispatcher.py`
- `_docs/AVAILABLE_TOOLS_SUMMARY.md`

---

## Planned Work

### New Files To Create

- `server/adapters/mcp/platform/capability_manifest.py`
- `server/adapters/mcp/discovery/tool_inventory.py`
- `server/adapters/mcp/discovery/taxonomy.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`

### Existing Files To Update

- `server/router/infrastructure/metadata_loader.py`
  - include every router-callable family that needs search enrichment data
- `server/router/infrastructure/tools_metadata/_schema.json`
  - keep router-focused fields router-focused; do not make it the canonical audience/visibility registry

### Ownership Rule

The canonical source for:

- audience
- phase tags
- public aliases
- pinned defaults
- hidden-from-search defaults

belongs in the platform capability manifest, not in router metadata.

---

## Pseudocode

```python
@dataclass
class DiscoveryEntry:
    tool_name: str
    category: str
    tags: set[str]
    aliases: list[str]
    pinned: bool
    hidden_from_search: bool
```

---

## Atomic Work Items

1. Define the shared platform manifest for public capability metadata.
2. Build discovery inventory from manifest + docstrings + schemas + optional router hints.
3. Keep router metadata as enrichment only.
4. Add tests proving every public and router-callable capability is represented exactly once.

---

## Acceptance Criteria

- discovery inventory covers all public and router-callable tools
- discovery grouping is no longer fragmented across docstrings, metadata, and ad hoc lists
