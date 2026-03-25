# TASK-118-04: Metadata, Docs, and Roundtrip Coverage

**Parent:** [TASK-118](./TASK-118_Scene_Render_World_And_Configuration_Wave.md)  
**Status:** 🚧 In Progress  
**Priority:** 🟡 Medium

**Progress Update:** Metadata, public docs, structured delivery, and unit regression coverage for `scene_configure` are now in place. The remaining gap is Blender-backed read/apply/read roundtrip coverage and the final explicit world/node-graph handoff documentation.

---

## Objective

Deliver the non-code surface for the new scene-tool wave and protect it with
roundtrip-oriented tests.

---

## Leaf Breakdown

| Leaf | Purpose |
|------|---------|
| [TASK-118-04-01](./TASK-118-04-01_Metadata_And_Public_Surface_Delivery.md) | Metadata, inventories, and public doc delivery |
| [TASK-118-04-02](./TASK-118-04-02_Unit_And_E2E_Roundtrip_Coverage.md) | Unit and Blender-backed roundtrip coverage |

---

## Acceptance Criteria

- scene config tools are represented consistently in metadata and docs
- read/apply/read roundtrip behavior is covered by regression tests
