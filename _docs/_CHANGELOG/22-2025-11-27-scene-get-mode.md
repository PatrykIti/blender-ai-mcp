# Changelog: Scene Get Mode Tool (TASK-014-1)

## Added
- `scene_get_mode` pipeline across Domain → Application → Adapter layers plus DI provider.
- Blender addon support: new `SceneHandler.get_mode`, RPC registration, and MCP adapter exposure with descriptive output.
- Unit tests for Blender addon handler and application handler, ensuring deterministic mode reporting.

## Documentation
- Updated README roadmap (Phase 7), architecture docs, `_docs/_ADDON`, `_docs/_MCP_SERVER`, and tool summaries.
- Recorded task completion details in `_docs/_TASKS` and new changelog index entry.

## Testing
- `poetry run pytest`
