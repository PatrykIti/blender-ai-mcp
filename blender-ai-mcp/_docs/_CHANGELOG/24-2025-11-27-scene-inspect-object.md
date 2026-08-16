# Changelog: Scene Inspect Object Tool (TASK-014-3)

## Added
- Extended scene domain/application interfaces with `inspect_object`, and added new MCP tool returning multi-section summaries.
- Blender addon implementation gathers transforms, collections, materials, modifiers, mesh stats (via evaluated mesh), and custom properties; registered RPC endpoint.

## Documentation
- Updated README Phase 7 checklist, scene architecture docs, addon + MCP docs, available tools summary, and task board.

## Testing
- `PYTHONPATH=. poetry run pytest`
- Added/updated tests: `tests/test_scene_mode.py`, `tests/test_scene_get_mode_handler.py`.
