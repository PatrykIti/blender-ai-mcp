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

- `server/adapters/mcp/discovery/tool_inventory.py`
- `server/adapters/mcp/discovery/taxonomy.py`
- `tests/unit/adapters/mcp/test_tool_inventory.py`

### Existing Files To Update

- `server/router/infrastructure/metadata_loader.py`
  - include every MCP-facing family that should participate in discovery
- `server/router/infrastructure/tools_metadata/_schema.json`
  - extend the schema with discovery-specific fields such as tags, aliases, pinned, audience, and hidden-from-search flags

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

## Acceptance Criteria

- discovery inventory covers all public and router-callable tools
- discovery grouping is no longer fragmented across docstrings, metadata, and ad hoc lists
