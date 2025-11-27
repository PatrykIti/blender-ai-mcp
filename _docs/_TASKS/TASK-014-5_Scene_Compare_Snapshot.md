# TASK-014-5: Scene Compare Snapshot Tool

**Status:** ⏳ To Do  
**Priority:** 🟡 Medium  
**Phase:** Phase 7 - Introspection & Listing APIs

## 🎯 Objective
Build a comparison tool that takes two snapshots (from TASK-014-4) and returns a structured diff summary (added/removed objects, transform deltas, modifier changes). This lets LLMs verify whether operations achieved expected results without relying on viewport images.

## 🏗️ Architecture Requirements
### 1. Domain Layer (`server/domain/tools/scene_compare_snapshot.py`)
- Define `SceneSnapshotDiffRequest` with fields: `baseline_snapshot: str`, `target_snapshot: str`, optional `ignore_minor_transforms: float` threshold.
- Define `SceneSnapshotDiff` response listing sections (objects_added, objects_removed, modified_objects with details).
- Interface `ISceneCompareSnapshotTool.compare(request) -> SceneSnapshotDiff`.

### 2. Application Layer (`server/application/handlers/scene_compare_snapshot_handler.py`)
- Handler validates JSON inputs (snapshots produced earlier), delegates to RPC `scene.compare_snapshot` or performs diff locally if more efficient.
- Provide formatting helper summarizing changes in human-readable bullet list.

### 3. Adapter Layer
- Register MCP tool `scene_compare_snapshot(baseline_snapshot: str, target_snapshot: str, ignore_minor_transforms: float = 0.0)`.
- Docstring: explain expected snapshot format (JSON strings) and caution about payload size.

### 4. Blender Addon API / Server Logic
- Decide where diffing lives: easiest is to compute diff on server side (Python) without Blender, so add pure-Python module under `server/application/services/snapshot_diff.py`.
- If addon must assist (e.g., verifying live scene), keep RPC endpoint minimal.

### 5. Infrastructure
- Update DI to wire new handler; ensure any helper services are registered as singletons.

## ✅ Deliverables
- Domain contracts + Pydantic models.
- Application handler + diff service implementation.
- MCP adapter entry with validations (reject empty snapshots).
- Documentation/changelog + README update referencing dependency on TASK-014-4.

## 🧪 Testing
- Create two snapshots around a modeling change and ensure diff reports modifications accurately.
- Edge cases: identical snapshots -> "No changes"; missing keys -> helpful error.

## 📚 References
- `_docs/TOOLS_ARCHITECTURE_DEEP_DIVE.md`
- TASK-014-4 snapshot structure.
