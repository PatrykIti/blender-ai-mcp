# Changelog: Scene Compare Snapshot Tool (TASK-014-5)

## Added
- Server-side snapshot diff service (`server/application/services/snapshot_diff.py`) that compares two JSON snapshots and returns structured diff (objects added/removed/modified).
- MCP tool `scene_compare_snapshot` with support for ignoring minor transform changes via threshold parameter.
- No RPC endpoint required - diffing performed entirely on MCP server side without Blender involvement.

## Documentation
- Updated TASK-014-5 status to Done, task board statistics, scene architecture docs.
- Added `scene_compare_snapshot` to available tools summary.

## Testing
- Manual testing recommended: create two snapshots around modeling changes, verify diff accuracy.
- Edge cases: identical snapshots return "No changes", missing keys return helpful errors.

## Version
1.9.5
