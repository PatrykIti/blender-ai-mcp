# Changelog: Scene Snapshot State Tool (TASK-014-4)

## Added
- Extended scene domain/application interfaces with `snapshot_state`, and added new MCP tool capturing JSON snapshots of scene state.
- Blender addon implementation iterates all objects in deterministic order, captures transforms, hierarchy, modifiers, selection state, with optional mesh stats and materials; computes SHA256 hash for change detection.
- RPC endpoint `scene.snapshot_state` registered in `blender_addon/__init__.py`.

## Documentation
- Updated TASK-014-4 status to Done, task board statistics, scene architecture docs.
- Added `scene_snapshot_state` to available tools summary.

## Testing
- Manual testing recommended: capture snapshots in simple scene, verify JSON output and hash stability.

## Version
1.9.4
