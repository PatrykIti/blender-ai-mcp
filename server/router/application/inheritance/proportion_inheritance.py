"""
Proportion Inheritance.

Enables workflows to inherit and combine proportion rules from similar workflows.
When modeling an unknown object (e.g., "chair"), this module can:
1. Find similar workflows (table, tower)
2. Extract proportion rules from each
3. Combine rules with weighted inheritance

TASK-046-4
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ProportionRule:
    """A single proportion rule.

    Attributes:
        name: Rule name (e.g., "bevel_ratio", "inset_ratio").
        value: The proportion value.
        source_workflow: Which workflow this came from.
        weight: Weight for combining (from similarity score).
        description: Human-readable description.
    """

    name: str
    value: float
    source_workflow: str
    weight: float = 1.0
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "source_workflow": self.source_workflow,
            "weight": self.weight,
            "description": self.description,
        }


@dataclass
class InheritedProportions:
    """Collection of inherited proportion rules.

    Combines rules from multiple workflows with weighted averaging.
    """

    rules: Dict[str, ProportionRule] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    total_weight: float = 0.0

    def get(self, name: str, default: float = 0.0) -> float:
        """Get proportion value by name.

        Args:
            name: Rule name.
            default: Default value if rule not found.

        Returns:
            Proportion value.
        """
        if name in self.rules:
            return self.rules[name].value
        return default

    def has(self, name: str) -> bool:
        """Check if rule exists.

        Args:
            name: Rule name.

        Returns:
            True if rule exists.
        """
        return name in self.rules

    def to_dict(self) -> Dict[str, float]:
        """Convert to simple dict for parameter substitution.

        Returns:
            Dictionary of rule name -> value.
        """
        return {name: rule.value for name, rule in self.rules.items()}

    def to_full_dict(self) -> Dict[str, Any]:
        """Convert to full dictionary with metadata.

        Returns:
            Dictionary with all rule details.
        """
        return {
            "rules": {name: rule.to_dict() for name, rule in self.rules.items()},
            "sources": self.sources,
            "total_weight": self.total_weight,
        }


class ProportionInheritance:
    """Inherits and combines proportion rules from workflows.

    Proportion rules define relative sizes for modeling operations:
    - bevel_ratio: Edge bevel as % of smallest dimension
    - inset_ratio: Face inset as % of face size
    - extrude_ratio: Extrusion depth as % of object height
    - taper_ratio: Taper amount for tall objects

    Example:
        ```python
        inheritance = ProportionInheritance()

        # Get inherited proportions from similar workflows
        similar_workflows = [("table_workflow", 0.72), ("tower_workflow", 0.45)]
        inherited = inheritance.inherit_proportions(similar_workflows)

        # Apply to object dimensions
        dimensions = [0.5, 0.5, 0.9]  # chair-like
        applied = inheritance.apply_to_dimensions(inherited, dimensions)
        # Returns: {"bevel_ratio": 0.015, "leg_ratio": 0.04, ...}
        ```
    """

    # Standard proportion rules per workflow type
    # These define the "style" of each workflow
    WORKFLOW_PROPORTIONS: Dict[str, Dict[str, float]] = {
        "phone_workflow": {
            "bevel_ratio": 0.04,  # Subtle edge bevel
            "inset_ratio": 0.05,  # Screen border
            "extrude_ratio": 0.40,  # Screen depth
            "corner_radius": 0.02,  # Rounded corners
        },
        "tower_workflow": {
            "bevel_ratio": 0.02,  # Light bevel
            "taper_ratio": 0.15,  # Top narrower than base
            "segment_ratio": 0.25,  # Floor/level height
            "base_ratio": 1.2,  # Base wider than body
        },
        "table_workflow": {
            "bevel_ratio": 0.03,  # Edge bevel
            "leg_ratio": 0.08,  # Leg width vs top
            "top_thickness": 0.05,  # Top thickness ratio
            "leg_inset": 0.10,  # Leg distance from edge
        },
        "screen_cutout_workflow": {
            "inset_ratio": 0.03,  # Border width
            "extrude_ratio": 0.50,  # Screen depth
            "bevel_ratio": 0.005,  # Very subtle bevel
        },
        "chair_workflow": {
            "bevel_ratio": 0.025,  # Moderate bevel
            "leg_ratio": 0.06,  # Leg width
            "seat_thickness": 0.06,  # Seat thickness
            "back_height": 0.5,  # Back as ratio of total
            "leg_inset": 0.08,  # Leg distance from edge
        },
        "cabinet_workflow": {
            "bevel_ratio": 0.015,  # Light bevel
            "door_inset": 0.02,  # Door panel inset
            "shelf_thickness": 0.02,  # Shelf thickness
            "handle_offset": 0.05,  # Handle position
        },
    }

    def __init__(self):
        """Initialize proportion inheritance."""
        self._custom_proportions: Dict[str, Dict[str, float]] = {}

    def register_proportions(
        self,
        workflow_name: str,
        proportions: Dict[str, float],
    ) -> None:
        """Register custom proportions for a workflow.

        Args:
            workflow_name: Workflow name.
            proportions: Proportion rules dictionary.
        """
        self._custom_proportions[workflow_name] = proportions
        logger.debug(f"Registered custom proportions for {workflow_name}")

    def get_workflow_proportions(
        self,
        workflow_name: str,
    ) -> Dict[str, float]:
        """Get proportions for a specific workflow.

        Args:
            workflow_name: Workflow name.

        Returns:
            Proportion rules dict (empty if not found).
        """
        # Check custom first
        if workflow_name in self._custom_proportions:
            return self._custom_proportions[workflow_name]

        # Check built-in
        if workflow_name in self.WORKFLOW_PROPORTIONS:
            return self.WORKFLOW_PROPORTIONS[workflow_name]

        return {}

    def inherit_proportions(
        self,
        similar_workflows: List[Tuple[str, float]],
    ) -> InheritedProportions:
        """Inherit proportions from similar workflows.

        Combines proportion rules weighted by workflow similarity.
        Higher similarity = more weight in the combined result.

        Args:
            similar_workflows: List of (workflow_name, similarity) tuples.
                             Similarity should be 0.0 to 1.0.

        Returns:
            InheritedProportions with combined rules.
        """
        result = InheritedProportions()

        if not similar_workflows:
            return result

        # Collect all rules with weights
        weighted_rules: Dict[str, List[Tuple[float, float, str]]] = {}

        for workflow_name, similarity in similar_workflows:
            proportions = self.get_workflow_proportions(workflow_name)
            result.sources.append(workflow_name)
            result.total_weight += similarity

            for rule_name, value in proportions.items():
                if rule_name not in weighted_rules:
                    weighted_rules[rule_name] = []
                weighted_rules[rule_name].append((value, similarity, workflow_name))

        # Calculate weighted average for each rule
        for rule_name, values in weighted_rules.items():
            total_weight = sum(w for _, w, _ in values)
            if total_weight > 0:
                weighted_value = sum(v * w for v, w, _ in values) / total_weight

                # Use the highest-weight source as the main source
                main_source = max(values, key=lambda x: x[1])[2]

                result.rules[rule_name] = ProportionRule(
                    name=rule_name,
                    value=weighted_value,
                    source_workflow=main_source,
                    weight=total_weight / result.total_weight
                    if result.total_weight > 0
                    else 0,
                    description=f"Inherited from {main_source} (weighted avg)",
                )

        logger.debug(
            f"Inherited {len(result.rules)} proportion rules from "
            f"{len(result.sources)} workflows"
        )

        return result

    def apply_to_dimensions(
        self,
        proportions: InheritedProportions,
        dimensions: List[float],
    ) -> Dict[str, float]:
        """Apply proportions to object dimensions.

        Converts relative proportions to absolute values based on dimensions.

        Args:
            proportions: Inherited proportions.
            dimensions: Object dimensions [x, y, z] in Blender units.

        Returns:
            Dict of parameter name -> absolute value.
        """
        if len(dimensions) < 3:
            logger.warning("Dimensions must have at least 3 values [x, y, z]")
            return {}

        x, y, z = dimensions[:3]
        min_dim = min(x, y, z)
        min_xy = min(x, y)
        max_dim = max(x, y, z)

        result = {}

        for name, rule in proportions.rules.items():
            # Apply different formulas based on rule type
            if "bevel" in name or "corner" in name:
                # Bevel relative to smallest dimension
                result[name] = rule.value * min_dim
            elif "inset" in name or "border" in name:
                # Inset relative to XY dimensions
                result[name] = rule.value * min_xy
            elif "extrude" in name or "depth" in name:
                # Extrude relative to Z height
                result[name] = rule.value * z
            elif "thickness" in name:
                # Thickness relative to min dimension
                result[name] = rule.value * min_dim
            elif "taper" in name or "ratio" in name:
                # Keep as ratio (no scaling)
                result[name] = rule.value
            elif "leg" in name:
                # Leg dimensions relative to XY
                result[name] = rule.value * min_xy
            elif "height" in name:
                # Height relative to Z
                result[name] = rule.value * z
            elif "offset" in name:
                # Offset relative to min dimension
                result[name] = rule.value * min_dim
            else:
                # Default: relative to min dimension
                result[name] = rule.value * min_dim

        return result

    def get_dimension_context(
        self,
        dimensions: List[float],
    ) -> Dict[str, float]:
        """Get dimension context for expression evaluation.

        Creates a context dict with dimension-derived values
        that can be used in workflow expressions.

        Args:
            dimensions: Object dimensions [x, y, z].

        Returns:
            Context dict with min_dim, max_dim, etc.
        """
        if len(dimensions) < 3:
            return {}

        x, y, z = dimensions[:3]
        return {
            "x": x,
            "y": y,
            "z": z,
            "width": x,
            "height": y,
            "depth": z,
            "min_dim": min(x, y, z),
            "max_dim": max(x, y, z),
            "min_xy": min(x, y),
            "max_xy": max(x, y),
            "volume": x * y * z,
            "surface_area": 2 * (x * y + y * z + x * z),
        }

    def suggest_proportions_for_object(
        self,
        object_type: str,
        similar_workflows: List[Tuple[str, float]],
        dimensions: List[float],
    ) -> Dict[str, Any]:
        """Suggest proportions for a new object type.

        Combines inherited proportions with dimension analysis
        to suggest good starting parameters.

        Args:
            object_type: Description of the object (e.g., "chair").
            similar_workflows: Similar workflows with scores.
            dimensions: Object dimensions [x, y, z].

        Returns:
            Dict with suggested parameters and explanations.
        """
        inherited = self.inherit_proportions(similar_workflows)
        applied = self.apply_to_dimensions(inherited, dimensions)
        dim_context = self.get_dimension_context(dimensions)

        return {
            "object_type": object_type,
            "dimensions": {
                "x": dimensions[0] if len(dimensions) > 0 else 0,
                "y": dimensions[1] if len(dimensions) > 1 else 0,
                "z": dimensions[2] if len(dimensions) > 2 else 0,
            },
            "dimension_context": dim_context,
            "inherited_proportions": inherited.to_dict(),
            "applied_values": applied,
            "sources": inherited.sources,
            "total_confidence": inherited.total_weight,
        }

    def get_available_rules(self) -> List[str]:
        """Get list of all available proportion rule names.

        Returns:
            List of rule names across all workflows.
        """
        rules = set()
        for proportions in self.WORKFLOW_PROPORTIONS.values():
            rules.update(proportions.keys())
        for proportions in self._custom_proportions.values():
            rules.update(proportions.keys())
        return sorted(rules)

    def get_info(self) -> Dict[str, Any]:
        """Get inheritance system information.

        Returns:
            Dictionary with system info.
        """
        return {
            "builtin_workflows": list(self.WORKFLOW_PROPORTIONS.keys()),
            "custom_workflows": list(self._custom_proportions.keys()),
            "available_rules": self.get_available_rules(),
            "total_workflows": len(self.WORKFLOW_PROPORTIONS)
            + len(self._custom_proportions),
        }
