# TASK-023: Material Tools

**Status:** ✅ Done
**Priority:** 🟠 High
**Category:** Material Tools
**Completed:** 2025-11-29

---

## Overview

Implement material creation and manipulation tools for PBR workflows.

---

# TASK-023-1: material_create

**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Implement `material_create` to create new PBR materials with Principled BSDF shader.

## Architecture Requirements

### 1. Domain Layer (`server/domain/tools/material.py`)

Extend `IMaterialTool` interface:

```python
@abstractmethod
def create_material(
    self,
    name: str,
    base_color: List[float] = None,  # [R, G, B, A] 0-1
    metallic: float = 0.0,
    roughness: float = 0.5,
    emission_color: List[float] = None,
    emission_strength: float = 0.0,
    alpha: float = 1.0,
) -> str:
    pass
```

### 2. Adapter Layer

```python
@mcp.tool()
def material_create(
    ctx: Context,
    name: str,
    base_color: List[float] = None,
    metallic: float = 0.0,
    roughness: float = 0.5,
    emission_color: List[float] = None,
    emission_strength: float = 0.0,
    alpha: float = 1.0,
) -> str:
    """
    [OBJECT MODE][SAFE] Creates a new PBR material with Principled BSDF.

    Workflow: AFTER -> material_assign

    Args:
        name: Material name
        base_color: RGBA color [0-1] (default: [0.8, 0.8, 0.8, 1.0])
        metallic: Metallic value 0-1
        roughness: Roughness value 0-1
        emission_color: Emission RGB [0-1]
        emission_strength: Emission strength
        alpha: Alpha/opacity 0-1
    """
```

### 3. Blender Addon

```python
def create_material(self, name, base_color=None, metallic=0.0, roughness=0.5, ...):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")

    if base_color:
        bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness

    if emission_color:
        bsdf.inputs["Emission Color"].default_value = (*emission_color, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength

    if alpha < 1.0:
        mat.blend_method = 'BLEND'
        bsdf.inputs["Alpha"].default_value = alpha

    return f"Created material '{mat.name}'"
```

## Deliverables

- [x] Implementation + Tests
- [x] Documentation

---

# TASK-023-2: material_assign

**Status:** ✅ Done
**Priority:** 🟠 High

## Objective

Implement `material_assign` to assign materials to objects or specific faces.

## Architecture Requirements

### 1. Domain Layer

```python
@abstractmethod
def assign_material(
    self,
    material_name: str,
    object_name: str = None,  # If None, use active object
    slot_index: int = None,  # If None, create new slot or use first
    assign_to_selection: bool = False,  # In Edit Mode, assign to selected faces
) -> str:
    pass
```

### 2. Adapter Layer

```python
@mcp.tool()
def material_assign(
    ctx: Context,
    material_name: str,
    object_name: str = None,
    slot_index: int = None,
    assign_to_selection: bool = False,
) -> str:
    """
    [OBJECT MODE/EDIT MODE][SELECTION-BASED] Assigns material to object or selected faces.

    In Object Mode: Assigns material to entire object
    In Edit Mode with assign_to_selection=True: Assigns to selected faces only

    Workflow: BEFORE -> material_create, mesh_select

    Args:
        material_name: Name of existing material
        object_name: Target object (default: active object)
        slot_index: Material slot index (default: auto)
        assign_to_selection: If True and in Edit Mode, assign to selected faces
    """
```

### 3. Blender Addon

```python
def assign_material(self, material_name, object_name=None, slot_index=None, assign_to_selection=False):
    mat = bpy.data.materials.get(material_name)
    if not mat:
        return f"Material '{material_name}' not found"

    obj = bpy.data.objects.get(object_name) if object_name else bpy.context.active_object

    # Add material slot if needed
    if mat.name not in [s.material.name for s in obj.material_slots if s.material]:
        obj.data.materials.append(mat)

    if assign_to_selection and obj.mode == 'EDIT':
        # Find slot index
        for i, slot in enumerate(obj.material_slots):
            if slot.material == mat:
                obj.active_material_index = i
                bpy.ops.object.material_slot_assign()
                return f"Assigned '{material_name}' to selected faces"

    return f"Assigned '{material_name}' to '{obj.name}'"
```

## Deliverables

- [x] Implementation + Tests
- [x] Documentation

---

# TASK-023-3: material_set_params

**Status:** ✅ Done
**Priority:** 🟡 Medium

## Objective

Implement `material_set_params` to modify existing material parameters.

## Architecture Requirements

### 1. Domain Layer

```python
@abstractmethod
def set_material_params(
    self,
    material_name: str,
    base_color: List[float] = None,
    metallic: float = None,
    roughness: float = None,
    emission_color: List[float] = None,
    emission_strength: float = None,
    alpha: float = None,
    specular: float = None,
    subsurface: float = None,
) -> str:
    pass
```

### 2. Adapter Layer

```python
@mcp.tool()
def material_set_params(
    ctx: Context,
    material_name: str,
    base_color: List[float] = None,
    metallic: float = None,
    roughness: float = None,
    emission_color: List[float] = None,
    emission_strength: float = None,
    alpha: float = None,
) -> str:
    """
    [OBJECT MODE][SAFE] Modifies parameters of existing material.

    Only provided parameters are changed; others remain unchanged.

    Workflow: BEFORE -> material_list

    Args:
        material_name: Name of material to modify
        base_color: New RGBA color [0-1]
        metallic: New metallic value 0-1
        roughness: New roughness value 0-1
        emission_color: New emission RGB [0-1]
        emission_strength: New emission strength
        alpha: New alpha/opacity 0-1
    """
```

## Deliverables

- [x] Implementation + Tests
- [x] Documentation

---

# TASK-023-4: material_set_texture

**Status:** ✅ Done
**Priority:** 🟡 Medium

## Objective

Implement `material_set_texture` to bind image textures to material inputs.

## Architecture Requirements

### 1. Domain Layer

```python
@abstractmethod
def set_material_texture(
    self,
    material_name: str,
    texture_path: str,
    input_name: str = "Base Color",  # 'Base Color', 'Roughness', 'Normal', 'Metallic', etc.
    color_space: str = "sRGB",  # 'sRGB', 'Non-Color'
) -> str:
    pass
```

### 2. Adapter Layer

```python
@mcp.tool()
def material_set_texture(
    ctx: Context,
    material_name: str,
    texture_path: str,
    input_name: str = "Base Color",
    color_space: str = "sRGB",
) -> str:
    """
    [OBJECT MODE][SAFE] Binds image texture to material input.

    Automatically creates Image Texture node and connects to Principled BSDF.

    Workflow: BEFORE -> material_create

    Args:
        material_name: Target material name
        texture_path: Path to image file
        input_name: BSDF input ('Base Color', 'Roughness', 'Normal', 'Metallic', 'Emission Color')
        color_space: Color space ('sRGB' for color, 'Non-Color' for data maps)
    """
```

### 3. Blender Addon

```python
def set_material_texture(self, material_name, texture_path, input_name="Base Color", color_space="sRGB"):
    mat = bpy.data.materials.get(material_name)
    if not mat or not mat.use_nodes:
        return f"Material '{material_name}' not found or not using nodes"

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Load image
    img = bpy.data.images.load(texture_path)
    img.colorspace_settings.name = color_space

    # Create texture node
    tex_node = nodes.new("ShaderNodeTexImage")
    tex_node.image = img
    tex_node.location = (-300, 300)

    # Find BSDF and connect
    bsdf = nodes.get("Principled BSDF")

    if input_name == "Normal":
        # Need normal map node
        normal_node = nodes.new("ShaderNodeNormalMap")
        normal_node.location = (-100, 0)
        links.new(tex_node.outputs["Color"], normal_node.inputs["Color"])
        links.new(normal_node.outputs["Normal"], bsdf.inputs["Normal"])
    else:
        links.new(tex_node.outputs["Color"], bsdf.inputs[input_name])

    return f"Connected texture to '{input_name}' on '{material_name}'"
```

## Deliverables

- [x] Implementation + Tests
- [x] Documentation

---

## Summary

| Tool | Priority | Description |
|------|----------|-------------|
| `material_create` | 🟠 High | Create PBR material with Principled BSDF |
| `material_assign` | 🟠 High | Assign material to object/faces |
| `material_set_params` | 🟡 Medium | Modify material parameters |
| `material_set_texture` | 🟡 Medium | Bind image textures to material |
