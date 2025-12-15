# Router Architecture & Code Template
# (for blender-ai-mcp)

This file contains:
- router directory structure,
- code skeleton,
- base classes,
- implementation template.

**Key Concept**: Router is an INTELLIGENT SUPERVISOR over LLM tool calls,
not just an "intent matcher". It intercepts, corrects, expands, and overrides
tool calls before execution.

============================================================
# 1. DIRECTORY STRUCTURE
============================================================

router/
├── __init__.py
├── router.py                      # Main supervisor router
├── metadata_loader.py             # Tool metadata loading
├── classifier.py                  # Intent classification (TF-IDF/SVM)
├── embeddings.py                  # Semantic matching (LaBSE)
├── planner.py                     # Workflow planning
├── utils.py                       # Utilities
├── tools_metadata.json            # Tool definitions
│
├── interceptor/                   # NEW: LLM Tool Interception
│   ├── __init__.py
│   └── tool_interceptor.py
│
├── analyzers/                     # NEW: Context Analysis
│   ├── __init__.py
│   ├── scene_context_analyzer.py
│   └── geometry_pattern_detector.py
│
├── engines/                       # NEW: Correction & Override
│   ├── __init__.py
│   ├── tool_correction_engine.py
│   ├── tool_override_engine.py
│   ├── workflow_expansion_engine.py
│   └── error_firewall.py
│
└── models/
    └── (optionally) embedding_model/


============================================================
# 2. FILE: tools_metadata.json (template)
============================================================

[
  {
    "name": "mesh_extrude_region",
    "category": "mesh",
    "keywords": ["extrude", "pull", "extend", "face"],
    "description": "Extrudes selected geometry and optionally moves it.",
    "sample_prompts": [
      "extrude face",
      "pull the face outward",
      "extrude the face geometry"
    ]
  },
  {
    "name": "modeling_create_primitive",
    "category": "modeling",
    "keywords": ["cube", "box", "primitive", "create cube"],
    "description": "Creates a primitive object (Cube/Sphere/Cylinder/...).",
    "sample_prompts": [
      "add cube",
      "create a cube",
      "create a box"
    ]
  }
]


============================================================
# 3. FILE: metadata_loader.py
============================================================

import json
from pathlib import Path

class ToolMetadata:
    def __init__(self, data):
        self.name = data["name"]
        self.category = data["category"]
        self.keywords = data.get("keywords", [])
        self.description = data.get("description", "")
        self.sample_prompts = data.get("sample_prompts", [])

class MetadataLoader:
    def __init__(self, path="tools_metadata.json"):
        self.path = Path(path)
        self.tools = []

    def load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.tools = [ToolMetadata(item) for item in data]
        return self.tools

    def find_tool_by_name(self, name):
        for t in self.tools:
            if t.name == name:
                return t
        return None


============================================================
# 4. FILE: classifier.py (TF-IDF + SVM / LR)
============================================================

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

class IntentClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.labels = []

    def train(self, metadata):
        """
        metadata = list of ToolMetadata
        """
        corpus = []
        labels = []

        for tool in metadata:
            for prompt in tool.sample_prompts:
                corpus.append(prompt)
                labels.append(tool.name)

        self.vectorizer = TfidfVectorizer()
        X = self.vectorizer.fit_transform(corpus)

        self.model = LogisticRegression(max_iter=200)
        self.model.fit(X, labels)

        self.labels = labels

    def predict(self, text):
        if not self.model:
            raise RuntimeError("Classifier not trained.")
        vec = self.vectorizer.transform([text])
        return self.model.predict(vec)[0]


============================================================
# 5. FILE: embeddings.py (optional, offline)
============================================================

import numpy as np

class EmbeddingStore:
    def __init__(self):
        self.model = None  # load sentence-transformers model here
        self.index = []    # list of (tool_name, embedding_vector)

    def load_model(self):
        # lazy load
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def build_index(self, metadata):
        self.load_model()
        for tool in metadata:
            # combine sample_prompts into one description
            text = tool.description + " " + " ".join(tool.sample_prompts)
            emb = self.model.encode(text)
            self.index.append((tool.name, emb))

    def most_similar(self, text, top_k=1):
        if not self.model:
            self.load_model()

        query = self.model.encode(text)
        best = None
        best_score = -1

        for name, emb in self.index:
            score = np.dot(query, emb) / (np.linalg.norm(query)*np.linalg.norm(emb))
            if score > best_score:
                best_score = score
                best = name

        return best, best_score


============================================================
# 6. FILE: planner.py (workflow engine)
============================================================

class Planner:
    """
    Maps intent → sequence of tools.
    """

    def __init__(self):
        self.workflows = {
            "create_phone": [
                "modeling_create_primitive",
                "modeling_transform_object",
                "mesh_bevel",
                "mesh_inset",
                "mesh_extrude_region",
                "material_assign"
            ]
        }

    def get_workflow(self, intent):
        return self.workflows.get(intent, None)


============================================================
# 7. FILE: utils.py
============================================================

import re

def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9 ]+", "", text)
    return text


============================================================
# 8. FILE: interceptor/tool_interceptor.py (NEW)
============================================================

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class InterceptedToolCall:
    """Captured LLM tool call with metadata."""
    source: str  # "llm" or "router"
    tool_name: str
    params: Dict[str, Any]
    timestamp: datetime
    original_prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ToolInterceptor:
    """
    Intercepts all LLM tool calls before execution.
    Enables post-processing pipeline.
    """

    def __init__(self):
        self.intercepted_calls = []

    def intercept(self, tool_name: str, params: Dict[str, Any],
                  prompt: str = None) -> InterceptedToolCall:
        """Capture and log LLM tool call."""
        call = InterceptedToolCall(
            source="llm",
            tool_name=tool_name,
            params=params,
            timestamp=datetime.now(),
            original_prompt=prompt
        )
        self.intercepted_calls.append(call)
        return call

    def get_history(self, limit: int = 10):
        """Get recent intercepted calls for context."""
        return self.intercepted_calls[-limit:]


============================================================
# 9. FILE: analyzers/scene_context_analyzer.py (NEW)
============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class SceneContext:
    """Current Blender scene state."""
    active_object: Optional[str]
    selected_objects: List[str]
    mode: str  # OBJECT, EDIT, SCULPT, etc.
    dimensions: Dict[str, float]  # x, y, z
    proportions: Dict[str, Any]
    topology: Dict[str, int]
    materials: List[str]

class SceneContextAnalyzer:
    """
    Analyzes current Blender scene state.
    Uses RPC to query Blender.
    """

    def __init__(self, rpc_client):
        self.rpc = rpc_client

    def analyze(self) -> SceneContext:
        """Get full scene context."""
        # Query scene via RPC
        scene_data = self.rpc.send_request("scene_get_context", {})
        active = scene_data.get("active_object")

        dimensions = {"x": 1.0, "y": 1.0, "z": 1.0}
        topology = {"vertices": 0, "edges": 0, "faces": 0}

        if active:
            # Get object details
            obj_data = self.rpc.send_request("scene_inspect_object", {
                "object_name": active
            })
            dimensions = obj_data.get("dimensions", dimensions)
            topology = obj_data.get("topology", topology)

        proportions = self._calculate_proportions(dimensions)

        return SceneContext(
            active_object=active,
            selected_objects=scene_data.get("selected_objects", []),
            mode=scene_data.get("mode", "OBJECT"),
            dimensions=dimensions,
            proportions=proportions,
            topology=topology,
            materials=scene_data.get("materials", [])
        )

    def _calculate_proportions(self, dims: Dict[str, float]) -> Dict[str, Any]:
        """Calculate geometric proportions."""
        x, y, z = dims.get("x", 1), dims.get("y", 1), dims.get("z", 1)
        min_dim = min(x, y, z)
        max_dim = max(x, y, z)

        return {
            "aspect_xy": x / y if y > 0 else 1.0,
            "aspect_xz": x / z if z > 0 else 1.0,
            "aspect_yz": y / z if z > 0 else 1.0,
            "is_flat": z < min(x, y) * 0.2,
            "is_tall": z > max(x, y) * 2,
            "is_wide": x > max(y, z) * 2,
            "is_cubic": max_dim / min_dim < 1.5 if min_dim > 0 else False,
            "dominant_axis": "z" if z >= max(x, y) else ("x" if x >= y else "y")
        }


============================================================
# 10. FILE: analyzers/geometry_pattern_detector.py (NEW)
============================================================

from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class DetectedPattern:
    """Recognized geometry pattern."""
    name: str
    confidence: float  # 0.0 - 1.0
    suggested_workflow: Optional[str]
    metadata: Dict[str, Any]

class GeometryPatternDetector:
    """
    Detects common 3D modeling patterns from scene context.
    """

    # Pattern definitions
    PATTERNS = {
        "tower_like": {
            "check": lambda p: p["is_tall"],
            "workflow": "tower_workflow",
            "description": "Tall structure (height >> width)"
        },
        "phone_like": {
            "check": lambda p, d: (
                p["is_flat"] and
                0.4 < p["aspect_xy"] < 0.7 and
                d["z"] < 0.15
            ),
            "workflow": "phone_workflow",
            "description": "Flat rectangular (phone/tablet)"
        },
        "table_like": {
            "check": lambda p: p["is_flat"] and not p["is_tall"],
            "workflow": "furniture_workflow",
            "description": "Flat horizontal surface"
        },
        "pillar_like": {
            "check": lambda p: p["is_tall"] and p["is_cubic"],
            "workflow": "pillar_workflow",
            "description": "Tall cubic structure"
        },
        "wheel_like": {
            "check": lambda p: p["is_flat"] and abs(p["aspect_xy"] - 1.0) < 0.1,
            "workflow": "wheel_workflow",
            "description": "Flat circular shape"
        }
    }

    def detect(self, proportions: Dict[str, Any],
               dimensions: Dict[str, float]) -> List[DetectedPattern]:
        """Detect all matching patterns."""
        detected = []

        for name, pattern in self.PATTERNS.items():
            try:
                check_fn = pattern["check"]
                # Try with both args, fallback to just proportions
                try:
                    matches = check_fn(proportions, dimensions)
                except TypeError:
                    matches = check_fn(proportions)

                if matches:
                    detected.append(DetectedPattern(
                        name=name,
                        confidence=0.8,  # TODO: calculate based on how well it matches
                        suggested_workflow=pattern.get("workflow"),
                        metadata={"description": pattern["description"]}
                    ))
            except Exception:
                continue

        return detected

    def get_primary_pattern(self, proportions: Dict[str, Any],
                           dimensions: Dict[str, float]) -> Optional[DetectedPattern]:
        """Get the most confident pattern match."""
        patterns = self.detect(proportions, dimensions)
        if patterns:
            return max(patterns, key=lambda p: p.confidence)
        return None


============================================================
# 11. FILE: engines/tool_correction_engine.py (NEW)
============================================================

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class CorrectedToolCall:
    """Tool call after correction."""
    tool_name: str
    params: Dict[str, Any]
    corrections_applied: List[str]
    original_params: Dict[str, Any]

class ToolCorrectionEngine:
    """
    Fixes incorrect or incomplete LLM tool calls.
    """

    # Parameter limits
    PARAM_LIMITS = {
        "bevel_width": (0.001, 10.0),
        "bevel_segments": (1, 10),
        "extrude_depth": (-100.0, 100.0),
        "inset_thickness": (0.001, 10.0),
        "subdivide_cuts": (1, 6),
        "decimate_ratio": (0.01, 1.0),
    }

    # Mode requirements
    MODE_REQUIREMENTS = {
        "mesh_": "EDIT",
        "modeling_": "OBJECT",
        "sculpt_": "SCULPT",
    }

    def __init__(self, scene_context=None):
        self.scene_context = scene_context

    def correct(self, tool_name: str, params: Dict[str, Any],
                mode: str = "OBJECT") -> Tuple[List[CorrectedToolCall], List[str]]:
        """
        Correct tool call, returns (tool_sequence, pre_steps).

        Returns:
            - tool_sequence: List of corrected tool calls
            - pre_steps: List of tool names to execute before (mode switches, etc.)
        """
        corrections = []
        pre_steps = []
        corrected_params = params.copy()

        # 1. Parameter correction
        corrected_params, param_corrections = self._correct_params(
            tool_name, corrected_params
        )
        corrections.extend(param_corrections)

        # 2. Mode correction
        required_mode = self._get_required_mode(tool_name)
        if required_mode and mode != required_mode:
            pre_steps.append(f"system_set_mode:{required_mode}")
            corrections.append(f"mode_switch:{mode}->{required_mode}")

        # 3. Selection correction (for mesh tools)
        if tool_name.startswith("mesh_") and self._needs_selection(tool_name):
            if not self._has_selection():
                pre_steps.append("mesh_select:all")
                corrections.append("auto_select_all")

        result = CorrectedToolCall(
            tool_name=tool_name,
            params=corrected_params,
            corrections_applied=corrections,
            original_params=params
        )

        return [result], pre_steps

    def _correct_params(self, tool_name: str,
                       params: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """Clamp parameters to valid ranges."""
        corrections = []
        corrected = params.copy()

        for param_key, value in params.items():
            limit_key = f"{param_key}"
            if limit_key in self.PARAM_LIMITS:
                min_val, max_val = self.PARAM_LIMITS[limit_key]
                if isinstance(value, (int, float)):
                    clamped = max(min_val, min(max_val, value))
                    if clamped != value:
                        corrected[param_key] = clamped
                        corrections.append(f"clamped:{param_key}:{value}->{clamped}")

        return corrected, corrections

    def _get_required_mode(self, tool_name: str) -> Optional[str]:
        """Get required Blender mode for tool."""
        for prefix, mode in self.MODE_REQUIREMENTS.items():
            if tool_name.startswith(prefix):
                return mode
        return None

    def _needs_selection(self, tool_name: str) -> bool:
        """Check if tool requires selection."""
        selection_tools = [
            "mesh_extrude_region", "mesh_bevel", "mesh_inset",
            "mesh_delete", "mesh_duplicate", "mesh_transform"
        ]
        return any(tool_name.startswith(t) for t in selection_tools)

    def _has_selection(self) -> bool:
        """Check if there's active selection (from scene context)."""
        if self.scene_context:
            return len(self.scene_context.selected_objects) > 0
        return True  # Assume yes if no context


============================================================
# 12. FILE: engines/tool_override_engine.py (NEW)
============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class OverrideDecision:
    """Result of override evaluation."""
    should_override: bool
    reason: str
    replacement_tools: List[Dict[str, Any]]

class ToolOverrideEngine:
    """
    Replaces LLM tool calls with better alternatives.
    """

    # Override rules: (condition) -> (replacement workflow)
    OVERRIDE_RULES = {
        # Pattern: if LLM sends X in context Y, replace with Z
        "extrude_for_screen": {
            "trigger": lambda t, ctx: (
                t == "mesh_extrude_region" and
                ctx.get("pattern") == "phone_like"
            ),
            "replacement": [
                {"tool": "mesh_inset", "params": {"thickness": 0.03}},
                {"tool": "mesh_extrude_region", "params": {"move": [0.0, 0.0, -0.02]}},
            ],
            "reason": "Expanded extrude to screen cutout workflow"
        },
        "subdivide_tower": {
            "trigger": lambda t, ctx: (
                t == "mesh_subdivide" and
                ctx.get("pattern") == "tower_like"
            ),
            "replacement": [
                {"tool": "mesh_subdivide", "params": {"number_cuts": 2}},
                {"tool": "mesh_select_targeted", "params": {"action": "loop", "edge_index": -1}},
                {"tool": "mesh_transform_selected", "params": {"scale": [0.8, 0.8, 1.0]}},
            ],
            "reason": "Added taper to tower subdivision"
        }
    }

    def evaluate(self, tool_name: str, params: Dict[str, Any],
                 context: Dict[str, Any]) -> OverrideDecision:
        """
        Evaluate if tool should be overridden.

        Args:
            tool_name: Original tool name
            params: Original parameters
            context: Scene context including detected patterns

        Returns:
            OverrideDecision with replacement if applicable
        """
        for rule_name, rule in self.OVERRIDE_RULES.items():
            try:
                if rule["trigger"](tool_name, context):
                    return OverrideDecision(
                        should_override=True,
                        reason=rule["reason"],
                        replacement_tools=rule["replacement"]
                    )
            except Exception:
                continue

        return OverrideDecision(
            should_override=False,
            reason="No override needed",
            replacement_tools=[]
        )


============================================================
# 13. FILE: engines/workflow_expansion_engine.py (NEW)
============================================================

from typing import Dict, Any, List

class WorkflowExpansionEngine:
    """
    Transforms single tool calls into complete workflows.
    """

    # Workflow templates
    WORKFLOWS = {
        "phone_workflow": [
            {"tool": "modeling_create_primitive", "params": {"primitive_type": "Cube"}},
            {"tool": "modeling_transform_object", "params": {"name": "Cube", "scale": [0.4, 0.8, 0.05]}},
            {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
            {"tool": "mesh_select", "params": {"action": "all"}},
            {"tool": "mesh_bevel", "params": {"offset": 0.02, "segments": 3}},
            {"tool": "mesh_select", "params": {"action": "none"}},
            {"tool": "mesh_select_targeted", "params": {"action": "by_location", "axis": "Z", "min_coord": 0.0, "max_coord": 9999.0, "element_type": "FACE"}},
            {"tool": "mesh_inset", "params": {"thickness": 0.03}},
            {"tool": "mesh_extrude_region", "params": {"move": [0.0, 0.0, -0.02]}},
            {"tool": "system_set_mode", "params": {"mode": "OBJECT"}},
        ],
        "tower_workflow": [
            {"tool": "modeling_create_primitive", "params": {"primitive_type": "Cube"}},
            {"tool": "modeling_transform_object", "params": {"name": "Cube", "scale": [0.3, 0.3, 2.0]}},
            {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
            {"tool": "mesh_subdivide", "params": {"number_cuts": 3}},
            {"tool": "mesh_select_targeted", "params": {"action": "loop", "edge_index": -1}},
            {"tool": "mesh_transform_selected", "params": {"scale": [0.7, 0.7, 1.0]}},
            {"tool": "system_set_mode", "params": {"mode": "OBJECT"}},
        ],
        "screen_cutout_workflow": [
            {"tool": "mesh_select_targeted", "params": {"action": "by_location", "axis": "Z", "min_coord": 0.0, "max_coord": 9999.0, "element_type": "FACE"}},
            {"tool": "mesh_inset", "params": {"thickness": 0.05}},
            {"tool": "mesh_extrude_region", "params": {"move": [0.0, 0.0, -0.02]}},
            {"tool": "mesh_bevel", "params": {"offset": 0.005, "segments": 2}},
        ],
        "bevel_all_edges_workflow": [
            {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
            {"tool": "mesh_select", "params": {"action": "all"}},
            {"tool": "mesh_bevel", "params": {"offset": 0.02, "segments": 2}},
            {"tool": "system_set_mode", "params": {"mode": "OBJECT"}},
        ]
    }

    # Expansion rules: single tool -> expanded workflow
    EXPANSION_RULES = {
        "mesh_extrude_region": {
            "condition": lambda ctx: ctx.get("no_selection", False),
            "expansion": [
                {"tool": "mesh_select", "params": {"action": "all"}},
                {"tool": "mesh_extrude_region", "params": {"move": "$move"}},  # $ = inherit param
            ]
        }
    }

    def get_workflow(self, workflow_name: str) -> List[Dict[str, Any]]:
        """Get predefined workflow by name."""
        return self.WORKFLOWS.get(workflow_name, [])

    def expand(self, tool_name: str, params: Dict[str, Any],
               context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Expand single tool to workflow if applicable.

        Args:
            tool_name: Original tool
            params: Original parameters
            context: Scene context

        Returns:
            Expanded workflow or original tool as list
        """
        if tool_name in self.EXPANSION_RULES:
            rule = self.EXPANSION_RULES[tool_name]
            if rule["condition"](context):
                # Expand and substitute parameters
                expanded = []
                for step in rule["expansion"]:
                    step_params = {}
                    for k, v in step["params"].items():
                        if isinstance(v, str) and v.startswith("$"):
                            # Inherit from original params
                            param_name = v[1:]
                            step_params[k] = params.get(param_name, v)
                        else:
                            step_params[k] = v
                    expanded.append({
                        "tool": step["tool"],
                        "params": step_params
                    })
                return expanded

        # No expansion, return original
        return [{"tool": tool_name, "params": params}]


============================================================
# 14. FILE: engines/error_firewall.py (NEW)
============================================================

from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FirewallResult:
    """Result of firewall check."""
    allowed: bool
    action: str  # "allow", "block", "modify", "auto_fix"
    message: str
    modified_call: Optional[Dict[str, Any]] = None

class ErrorFirewall:
    """
    Blocks or fixes invalid operations before execution.
    """

    # Firewall rules
    RULES = {
        "mesh_in_object_mode": {
            "check": lambda t, m: t.startswith("mesh_") and m == "OBJECT",
            "action": "auto_fix",
            "fix": "switch_to_edit_mode",
            "message": "Mesh tool requires Edit mode - auto-switching"
        },
        "object_in_edit_mode": {
            "check": lambda t, m: t.startswith("modeling_") and m == "EDIT",
            "action": "auto_fix",
            "fix": "switch_to_object_mode",
            "message": "Modeling tool requires Object mode - auto-switching"
        },
        "extrude_no_selection": {
            "check": lambda t, ctx: (
                t == "mesh_extrude_region" and
                ctx.get("selection_count", 0) == 0
            ),
            "action": "auto_fix",
            "fix": "select_all_faces",
            "message": "Extrude requires selection - auto-selecting all faces"
        },
        "bevel_too_large": {
            "check": lambda t, p, ctx: (
                t == "mesh_bevel" and
                p.get("offset", 0) > ctx.get("min_dimension", 1) * 0.5
            ),
            "action": "modify",
            "message": "Bevel offset too large - clamping to safe value"
        },
        "delete_no_object": {
            "check": lambda t, ctx: (
                t == "scene_delete_object" and
                ctx.get("object_count", 0) == 0
            ),
            "action": "block",
            "message": "Cannot delete - no objects in scene"
        }
    }

    def __init__(self, scene_context=None):
        self.scene_context = scene_context or {}

    def check(self, tool_name: str, params: Dict[str, Any],
              mode: str = "OBJECT") -> FirewallResult:
        """
        Check if tool call should be allowed.

        Returns FirewallResult with action and optional fix.
        """
        ctx = {
            "mode": mode,
            "selection_count": len(self.scene_context.get("selected", [])),
            "object_count": self.scene_context.get("object_count", 1),
            "min_dimension": min(
                self.scene_context.get("dimensions", {}).get("x", 1),
                self.scene_context.get("dimensions", {}).get("y", 1),
                self.scene_context.get("dimensions", {}).get("z", 1)
            )
        }

        for rule_name, rule in self.RULES.items():
            try:
                check_fn = rule["check"]
                # Try different argument combinations
                try:
                    triggered = check_fn(tool_name, params, ctx)
                except TypeError:
                    try:
                        triggered = check_fn(tool_name, ctx)
                    except TypeError:
                        triggered = check_fn(tool_name, mode)

                if triggered:
                    return FirewallResult(
                        allowed=rule["action"] != "block",
                        action=rule["action"],
                        message=rule["message"],
                        modified_call=self._apply_fix(rule, tool_name, params, ctx)
                    )
            except Exception:
                continue

        return FirewallResult(
            allowed=True,
            action="allow",
            message="OK"
        )

    def _apply_fix(self, rule: Dict, tool_name: str,
                   params: Dict, ctx: Dict) -> Optional[Dict]:
        """Apply automatic fix if defined."""
        fix = rule.get("fix")
        if not fix:
            return None

        if fix == "switch_to_edit_mode":
            return {"pre_tool": "system_set_mode", "pre_params": {"mode": "EDIT"}}
        elif fix == "switch_to_object_mode":
            return {"pre_tool": "system_set_mode", "pre_params": {"mode": "OBJECT"}}
        elif fix == "select_all_faces":
            return {"pre_tool": "mesh_select", "pre_params": {"action": "all", "mode": "FACE"}}

        return None


============================================================
# 15. FILE: router.py (MAIN SUPERVISOR ROUTER - UPDATED)
============================================================

from metadata_loader import MetadataLoader
from classifier import IntentClassifier
from embeddings import EmbeddingStore
from planner import Planner
from utils import clean_text

# NEW imports
from interceptor.tool_interceptor import ToolInterceptor
from analyzers.scene_context_analyzer import SceneContextAnalyzer
from analyzers.geometry_pattern_detector import GeometryPatternDetector
from engines.tool_correction_engine import ToolCorrectionEngine
from engines.tool_override_engine import ToolOverrideEngine
from engines.workflow_expansion_engine import WorkflowExpansionEngine
from engines.error_firewall import ErrorFirewall

class SupervisorRouter:
    """
    Intelligent Router acting as supervisor over LLM tool calls.

    Pipeline:
    1. Intercept LLM tool call
    2. Analyze scene context
    3. Detect geometry patterns
    4. Apply corrections
    5. Check for overrides
    6. Expand to workflow if needed
    7. Firewall check
    8. Execute
    """

    def __init__(self, rpc_client=None):
        # Core components (existing)
        self.metadata_loader = MetadataLoader()
        self.tools = self.metadata_loader.load()
        self.classifier = IntentClassifier()
        self.classifier.train(self.tools)
        self.embeddings = EmbeddingStore()
        self.embeddings.build_index(self.tools)
        self.planner = Planner()

        # NEW: Supervisor components
        self.interceptor = ToolInterceptor()
        self.context_analyzer = SceneContextAnalyzer(rpc_client) if rpc_client else None
        self.pattern_detector = GeometryPatternDetector()
        self.correction_engine = ToolCorrectionEngine()
        self.override_engine = ToolOverrideEngine()
        self.expansion_engine = WorkflowExpansionEngine()
        self.firewall = ErrorFirewall()

        self.rpc = rpc_client

    def process_llm_tool_call(self, tool_name: str, params: dict,
                               original_prompt: str = None) -> list:
        """
        Main entry point for LLM tool calls.
        Applies full supervisor pipeline.

        Args:
            tool_name: Tool name from LLM
            params: Parameters from LLM
            original_prompt: Original user prompt (for context)

        Returns:
            List of tool calls to execute (may be expanded/corrected)
        """
        # 1. Intercept
        intercepted = self.interceptor.intercept(tool_name, params, original_prompt)

        # 2. Analyze scene context
        scene_ctx = None
        if self.context_analyzer:
            scene_ctx = self.context_analyzer.analyze()
            self.correction_engine.scene_context = scene_ctx
            self.firewall.scene_context = {
                "selected": scene_ctx.selected_objects,
                "dimensions": scene_ctx.dimensions,
                "object_count": 1 if scene_ctx.active_object else 0
            }

        # 3. Detect patterns
        pattern = None
        if scene_ctx:
            pattern = self.pattern_detector.get_primary_pattern(
                scene_ctx.proportions,
                scene_ctx.dimensions
            )

        context = {
            "pattern": pattern.name if pattern else None,
            "mode": scene_ctx.mode if scene_ctx else "OBJECT",
            "no_selection": len(scene_ctx.selected_objects) == 0 if scene_ctx else False
        }

        # 4. Check override
        override = self.override_engine.evaluate(tool_name, params, context)
        if override.should_override:
            return override.replacement_tools

        # 5. Apply corrections
        corrected, pre_steps = self.correction_engine.correct(
            tool_name, params,
            mode=context["mode"]
        )

        # 6. Expand workflow
        final_tools = []
        for tool_call in corrected:
            expanded = self.expansion_engine.expand(
                tool_call.tool_name,
                tool_call.params,
                context
            )
            final_tools.extend(expanded)

        # 7. Firewall each tool
        approved_tools = []
        for tool in final_tools:
            fw_result = self.firewall.check(
                tool["tool"],
                tool["params"],
                mode=context["mode"]
            )
            if fw_result.allowed:
                if fw_result.modified_call:
                    # Insert pre-tool if needed
                    approved_tools.append({
                        "tool": fw_result.modified_call["pre_tool"],
                        "params": fw_result.modified_call["pre_params"]
                    })
                approved_tools.append(tool)

        # Add pre-steps at beginning
        result = []
        for step in pre_steps:
            parts = step.split(":")
            result.append({"tool": parts[0], "params": {"mode": parts[1]} if len(parts) > 1 else {}})
        result.extend(approved_tools)

        return result

    def route(self, prompt: str) -> list:
        """
        Original routing method for offline intent matching.
        Used when no LLM is involved.
        """
        text = clean_text(prompt)

        try:
            intent_or_tool = self.classifier.predict(text)
        except:
            intent_or_tool = None

        emb_tool, score = self.embeddings.most_similar(text)
        if score > 0.40:
            final_tool = emb_tool
        else:
            final_tool = intent_or_tool or emb_tool

        workflow = self.planner.get_workflow(final_tool)
        if workflow:
            return workflow

        return [final_tool]


============================================================
# 16. USAGE EXAMPLE (in MCP server)
============================================================

# Initialize router with RPC client
from server.adapters.rpc.client import RpcClient

rpc_client = RpcClient(host="127.0.0.1", port=8765)
router = SupervisorRouter(rpc_client)

# Example 1: Process LLM tool call (supervisor mode)
llm_tool_call = {
    "tool": "mesh_extrude_region",
    "params": {"move": [0.0, 0.0, 0.5]}
}

corrected_tools = router.process_llm_tool_call(
    tool_name=llm_tool_call["tool"],
    params=llm_tool_call["params"],
    prompt="extrude the top face"
)

print("Tools to execute:", corrected_tools)
# Output might be:
# [
#   {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
#   {"tool": "mesh_select", "params": {"action": "all"}},
#   {"tool": "mesh_extrude_region", "params": {"move": [0.0, 0.0, 0.5]}}
# ]

# Example 2: Offline routing (no LLM)
prompt = "create a phone with rounded edges"
tools_to_run = router.route(prompt)
print("Offline route:", tools_to_run)


============================================================
# END
============================================================
