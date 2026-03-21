# TASK-084-01: Public Capability Inventory and Discovery Taxonomy

**Parent:** [TASK-084](./TASK-084_Dynamic_Tool_Discovery.md)  
**Status:** ⬜ Planned  
**Priority:** 🔴 High  
**Depends On:** [TASK-083-02](./TASK-083-02_Provider_Based_Component_Inventory.md)

---

## Objective

Create one canonical discovery inventory for the public MCP-facing capability surface: categories, tags, aliases, and visibility flags for capabilities that should actually participate in public discovery.

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
  - expose router hints only as optional enrichment
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

Internal router / dispatcher aliases are not part of the public discovery taxonomy by default.
If an internal alias needs metadata for routing or compatibility, keep it in a separate internal execution map.

---

## Pseudocode

```python
@dataclass
class DiscoveryEntry:
    public_name: str
    category: str
    tags: set[str]
    aliases: list[str]
    pinned: bool
    hidden_from_search: bool
```

---

## Atomic Work Items

1. Define the shared platform manifest for public capability metadata only.
2. Build discovery inventory from public manifest + docstrings + schemas + optional router hints.
3. Keep router metadata as enrichment only.
4. Keep dispatcher/router compatibility names out of the public discovery inventory unless they are explicitly exposed on a public surface.
5. Add tests proving every public MCP-visible capability is represented exactly once.

---

## Layered Subtasks

| ID | Title | Focus |
|----|-------|-------|
| [TASK-084-01-01](./TASK-084-01-01_Core_Inventory_Normalization_Discovery_Taxonomy.md) | Core Tool Inventory Normalization and Discovery Taxonomy | Core implementation layer |
| [TASK-084-01-02](./TASK-084-01-02_Tests_Inventory_Normalization_Discovery_Taxonomy.md) | Tests and Docs Tool Inventory Normalization and Discovery Taxonomy | Tests, docs, and QA |

---

## Acceptance Criteria

- discovery inventory covers all public MCP-visible capabilities on the shaped surface
- internal router / dispatcher aliases are either excluded from discovery or explicitly marked non-discoverable
- discovery grouping is no longer fragmented across docstrings, metadata, and ad hoc lists
