# Changelog: Scene List Selection Tool (TASK-014-2)

## Added
- `scene_list_selection` tooling end-to-end (domain interface extensions, SceneToolHandler wiring, MCP adapter output, Blender addon implementation with Edit Mode counts, RPC registration).
- Extended `scene_get_mode` implementation to align with shared scene handler abstraction and deterministic dict payloads.

## Documentation
- Updated README Phase 7 checklist plus `_docs` knowledge base (Scene architecture, Available Tools summary, Addon/MCP docs, task file, changelog index).

## Testing
- `PYTHONPATH=. poetry run pytest`
- Added/updated tests: `tests/test_scene_mode.py`, `tests/test_scene_get_mode_handler.py`.
