# Curve Tools Architecture

Curve tools operate on curve objects (Bezier, NURBS, etc.).
**Context:** These tools primarily operate in **Object Mode**.

---

# 1. curve_create ✅ Done

Creates a curve primitive object.

**Tag:** `[OBJECT MODE][SAFE]`

Args:
- curve_type: str ('BEZIER', 'NURBS', 'PATH', 'CIRCLE') - Type of curve to create
- location: [x, y, z] (optional) - Position for the new curve

Example:
```json
{
  "tool": "curve_create",
  "args": {
    "curve_type": "BEZIER",
    "location": [0, 0, 0]
  }
}
```

Curve Types:
- **BEZIER**: Bezier curve with control handles - best for manual editing
- **NURBS**: NURBS curve - smooth mathematical curves
- **PATH**: NURBS path - optimized for animation follow paths
- **CIRCLE**: Bezier circle - closed circular curve

Use Cases:
- Creating profiles for lathe/spin operations
- Animation paths for follow path constraints
- Guides for array modifier curves
- Profile curves for bevel/taper

---

# 2. curve_to_mesh ✅ Done

Converts a curve object to mesh geometry.

**Tag:** `[OBJECT MODE][DESTRUCTIVE]`

Args:
- object_name: str - Name of the curve object to convert

Example:
```json
{
  "tool": "curve_to_mesh",
  "args": {
    "object_name": "BezierCurve"
  }
}
```

Supported Object Types:
- CURVE (Bezier, NURBS)
- SURFACE (NURBS surfaces)
- FONT (Text objects)

Use Cases:
- Converting curve profiles to editable mesh
- Preparing curves for boolean operations
- Finalizing text/font objects for export
- Creating mesh geometry from procedural curves

Notes:
- This is a **destructive** operation - the curve data is replaced with mesh data
- For non-destructive workflow, use `modeling_add_modifier` with a curve modifier instead
- Resolution of the resulting mesh depends on curve's resolution settings before conversion

---

# 3. curve_get_data ✅ Done

Returns curve splines, points, and settings for reconstruction.

**Tag:** `[OBJECT MODE][READ-ONLY][SAFE]`

Args:
- object_name: str - Name of the curve object to inspect

Example:
```json
{
  "tool": "curve_get_data",
  "args": {
    "object_name": "BezierCurve"
  }
}
```

Returns (example):
```json
{
  "object_name": "BezierCurve",
  "dimensions": "3D",
  "bevel_depth": 0.0,
  "extrude": 0.0,
  "splines": [
    {
      "type": "BEZIER",
      "use_cyclic_u": false,
      "bezier_points": [
        {
          "co": [0.0, 0.0, 0.0],
          "handle_left": [-1.0, 0.0, 0.0],
          "handle_right": [1.0, 0.0, 0.0],
          "handle_left_type": "AUTO",
          "handle_right_type": "AUTO"
        }
      ]
    }
  ]
}
```

Use Cases:
- Exact curve reconstruction in YAML workflows
- Copying spline shapes between scenes
- Validating curve settings before conversion

Notes:
- Returns Bezier handle positions for BEZIER splines.
- NURBS/POLY splines return control points with weights when available.

---

# Workflow Examples

## Creating a Vase with Spin

```python
# 1. Create profile curve
curve_create(curve_type="BEZIER", location=[1, 0, 0])

# 2. Convert to mesh
curve_to_mesh(object_name="BezierCurve")

# 3. Select all vertices
mesh_select(action="all")

# 4. Spin around Z axis
mesh_spin(steps=32, axis="Z", center=[0, 0, 0])
```

## Creating Text as Mesh

```python
# Assume text object "MyText" already exists

# 1. Convert to mesh
curve_to_mesh(object_name="MyText")

# Now you can use mesh tools on the text
```

---

# Rules

1. **Prefix `curve_`**: All curve tools must start with this prefix.
2. **Object Mode**: Curve creation and conversion operate in Object Mode.
3. **Destructive Conversion**: `curve_to_mesh` permanently converts - consider alternatives for non-destructive workflows.
