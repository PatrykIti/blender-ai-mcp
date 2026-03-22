# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: BUSL-1.1

"""
MCP tool registration modules ("areas").

Author: Patryk Ciechański (PatrykIti)
"""

# Compatibility bootstrap for the current runtime. TASK-083-02/03 gradually
# replaces this side-effect import path with explicit registrars and providers.
from . import armature
from . import baking
from . import collection
from . import curve
from . import extraction
from . import lattice
from . import material
from . import mesh
from . import modeling
from . import router
from . import scene
from . import sculpt
from . import system
from . import uv
from . import workflow_catalog

from .mesh import register_mesh_tools
from .modeling import register_modeling_tools
from .router import register_router_tools
from .scene import register_scene_tools
from .workflow_catalog import register_workflow_tools
from .armature import register_armature_tools
from .baking import register_baking_tools
from .collection import register_collection_tools
from .curve import register_curve_tools
from .extraction import register_extraction_tools
from .lattice import register_lattice_tools
from .material import register_material_tools
from .sculpt import register_sculpt_tools
from .system import register_system_tools
from .text import register_text_tools
from .uv import register_uv_tools

__all__ = [
    "register_armature_tools",
    "register_baking_tools",
    "register_collection_tools",
    "register_curve_tools",
    "register_extraction_tools",
    "register_lattice_tools",
    "register_material_tools",
    "register_mesh_tools",
    "register_modeling_tools",
    "register_router_tools",
    "register_sculpt_tools",
    "register_scene_tools",
    "register_system_tools",
    "register_text_tools",
    "register_uv_tools",
    "register_workflow_tools",
]
