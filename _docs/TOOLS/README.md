# Tool Architecture Documentation

Maintainer-facing architecture notes for the tool families underneath the Blender AI MCP server.

These docs are **not** the canonical public-surface policy.
They explain the implementation substrate: atomic families, grouped tool families, and specialist domains that may be exposed differently depending on the MCP surface/profile.

Canonical policy and public-surface behavior live in:

- [`../_MCP_SERVER/TOOL_LAYERING_POLICY.md`](../_MCP_SERVER/TOOL_LAYERING_POLICY.md)
- [`../_MCP_SERVER/README.md`](../_MCP_SERVER/README.md)
- [`../_ROUTER/RESPONSIBILITY_BOUNDARIES.md`](../_ROUTER/RESPONSIBILITY_BOUNDARIES.md)

## 📚 Topic Index

| Document | Scope |
|---|---|
| [SCENE_TOOLS_ARCHITECTURE.md](./SCENE_TOOLS_ARCHITECTURE.md) | Scene-level object management, viewport control, inspection, and context tools |
| [MODELING_TOOLS_ARCHITECTURE.md](./MODELING_TOOLS_ARCHITECTURE.md) | Object-mode creation, transforms, modifiers, and higher-level modeling actions |
| [MESH_TOOLS_ARCHITECTURE.md](./MESH_TOOLS_ARCHITECTURE.md) | Edit-mode mesh operations, grouped mesh entry tools, and low-level geometry editing |
| [MEGA_TOOLS_ARCHITECTURE.md](./MEGA_TOOLS_ARCHITECTURE.md) | Historical grouped-tool consolidation doc; current grouped public layer above internal atomic actions |
| [MATERIAL_TOOLS_ARCHITECTURE.md](./MATERIAL_TOOLS_ARCHITECTURE.md) | Material creation, assignment, parameter editing, and shader-related tool design |
| [UV_TOOLS_ARCHITECTURE.md](./UV_TOOLS_ARCHITECTURE.md) | UV map listing, unwrapping, packing, and seam workflows |
| [COLLECTION_TOOLS_ARCHITECTURE.md](./COLLECTION_TOOLS_ARCHITECTURE.md) | Blender collection hierarchy management and object membership operations |
| [CURVE_TOOLS_ARCHITECTURE.md](./CURVE_TOOLS_ARCHITECTURE.md) | Curve construction, conversion, and procedural curve-related tooling |
| [LATTICE_TOOLS_ARCHITECTURE.md](./LATTICE_TOOLS_ARCHITECTURE.md) | Lattice deformation workflows and supporting tool surface design |
| [SCULPT_TOOLS_ARCHITECTURE.md](./SCULPT_TOOLS_ARCHITECTURE.md) | Sculpt-mode brushes, automation helpers, and sculpt workflow considerations |
| [SYSTEM_TOOLS_ARCHITECTURE.md](./SYSTEM_TOOLS_ARCHITECTURE.md) | File, undo/redo, mode, and project-level system operations |
| [EXPORT_TOOLS_ARCHITECTURE.md](./EXPORT_TOOLS_ARCHITECTURE.md) | Export tool behavior, format handling, and output contracts |
| [EXTRACTION_TOOLS_ARCHITECTURE.md](./EXTRACTION_TOOLS_ARCHITECTURE.md) | Analysis and extraction tooling for reconstruction, auditing, and inspection-heavy flows |

## How To Use These Docs

- Start with the policy docs above if the change affects public exposure, goal-first flow, or verification behavior.
- Then open the tool family you are changing.
- Read these files as implementation/family docs, not as proof that every listed tool should be public by default.
- Cross-check the public MCP surface in [`../_MCP_SERVER/README.md`](../_MCP_SERVER/README.md) before changing tool exposure.
- If the change affects router behavior or metadata, continue with [`../_ROUTER/README.md`](../_ROUTER/README.md) and [`../_ROUTER/TOOLS/README.md`](../_ROUTER/TOOLS/README.md).
