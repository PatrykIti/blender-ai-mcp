"""
Proportion Resolver.

Resolves $AUTO_* parameters relative to object dimensions.
Provides smart defaults for common operations.

TASK-041-13
"""

import logging
from typing import Dict, Any, Optional, List, Union, Callable

logger = logging.getLogger(__name__)


class ProportionResolver:
    """Resolves parameters relative to object proportions.

    Provides $AUTO_* macros that calculate appropriate values
    based on object dimensions. This enables workflows to work
    well regardless of object scale.

    Supported macros:
    - $AUTO_BEVEL: 5% of smallest dimension
    - $AUTO_BEVEL_SMALL: 2% of smallest dimension
    - $AUTO_BEVEL_LARGE: 10% of smallest dimension
    - $AUTO_INSET: 3% of XY plane smallest dimension
    - $AUTO_INSET_THICK: 5% of XY plane smallest dimension
    - $AUTO_EXTRUDE: 10% of Z height
    - $AUTO_EXTRUDE_SMALL: 5% of Z height
    - $AUTO_EXTRUDE_DEEP: 20% of Z height
    - $AUTO_SCALE_SMALL: 80% of current size [x, y, z]
    - $AUTO_SCALE_TINY: 50% of current size [x, y, z]
    - $AUTO_OFFSET: 2% of smallest dimension
    - $AUTO_THICKNESS: 5% of depth (Z)
    - $AUTO_SCREEN_DEPTH: 50% of depth (for phone screens)

    Example:
        resolver = ProportionResolver()
        resolver.set_dimensions([2.0, 4.0, 0.5])
        resolver.resolve("$AUTO_BEVEL")  # -> 0.025 (5% of 0.5)
    """

    def __init__(self):
        """Initialize proportion resolver."""
        self._dimensions: Optional[List[float]] = None
        self._auto_params: Dict[str, Dict[str, Any]] = self._build_auto_params()

    def _build_auto_params(self) -> Dict[str, Dict[str, Any]]:
        """Build the auto-parameter definitions.

        Returns:
            Dictionary mapping $AUTO_* names to calculation functions.
        """
        return {
            # Bevel widths
            "$AUTO_BEVEL": {
                "calculation": self._calc_bevel,
                "description": "5% of smallest dimension",
                "returns": "float",
            },
            "$AUTO_BEVEL_SMALL": {
                "calculation": self._calc_bevel_small,
                "description": "2% of smallest dimension",
                "returns": "float",
            },
            "$AUTO_BEVEL_LARGE": {
                "calculation": self._calc_bevel_large,
                "description": "10% of smallest dimension",
                "returns": "float",
            },
            # Inset thicknesses
            "$AUTO_INSET": {
                "calculation": self._calc_inset,
                "description": "3% of XY plane smallest dimension",
                "returns": "float",
            },
            "$AUTO_INSET_THICK": {
                "calculation": self._calc_inset_thick,
                "description": "5% of XY plane smallest dimension",
                "returns": "float",
            },
            # Extrude distances
            "$AUTO_EXTRUDE": {
                "calculation": self._calc_extrude,
                "description": "10% of Z height (depth)",
                "returns": "float",
            },
            "$AUTO_EXTRUDE_SMALL": {
                "calculation": self._calc_extrude_small,
                "description": "5% of Z height (depth)",
                "returns": "float",
            },
            "$AUTO_EXTRUDE_DEEP": {
                "calculation": self._calc_extrude_deep,
                "description": "20% of Z height (depth)",
                "returns": "float",
            },
            "$AUTO_EXTRUDE_NEG": {
                "calculation": self._calc_extrude_neg,
                "description": "-10% of Z height (inward extrude)",
                "returns": "float",
            },
            # Scale factors
            "$AUTO_SCALE_SMALL": {
                "calculation": self._calc_scale_small,
                "description": "80% of current size [x, y, z]",
                "returns": "list",
            },
            "$AUTO_SCALE_TINY": {
                "calculation": self._calc_scale_tiny,
                "description": "50% of current size [x, y, z]",
                "returns": "list",
            },
            # Offsets and thicknesses
            "$AUTO_OFFSET": {
                "calculation": self._calc_offset,
                "description": "2% of smallest dimension",
                "returns": "float",
            },
            "$AUTO_THICKNESS": {
                "calculation": self._calc_thickness,
                "description": "5% of depth (Z)",
                "returns": "float",
            },
            # Phone-specific
            "$AUTO_SCREEN_DEPTH": {
                "calculation": self._calc_screen_depth,
                "description": "50% of depth (for phone screen cutout)",
                "returns": "float",
            },
            "$AUTO_SCREEN_DEPTH_NEG": {
                "calculation": self._calc_screen_depth_neg,
                "description": "-50% of depth (for inward screen)",
                "returns": "float",
            },
            # Loop cut positions (relative)
            "$AUTO_LOOP_POS": {
                "calculation": self._calc_loop_pos,
                "description": "0.8 position factor for loop cuts",
                "returns": "float",
            },
        }

    # Calculation methods
    def _calc_bevel(self) -> float:
        """Calculate standard bevel width (5% of min dim)."""
        return min(self._dimensions) * 0.05

    def _calc_bevel_small(self) -> float:
        """Calculate small bevel width (2% of min dim)."""
        return min(self._dimensions) * 0.02

    def _calc_bevel_large(self) -> float:
        """Calculate large bevel width (10% of min dim)."""
        return min(self._dimensions) * 0.10

    def _calc_inset(self) -> float:
        """Calculate inset thickness (3% of XY min)."""
        return min(self._dimensions[0], self._dimensions[1]) * 0.03

    def _calc_inset_thick(self) -> float:
        """Calculate thick inset (5% of XY min)."""
        return min(self._dimensions[0], self._dimensions[1]) * 0.05

    def _calc_extrude(self) -> float:
        """Calculate extrude distance (10% of Z)."""
        return self._dimensions[2] * 0.10

    def _calc_extrude_small(self) -> float:
        """Calculate small extrude distance (5% of Z)."""
        return self._dimensions[2] * 0.05

    def _calc_extrude_deep(self) -> float:
        """Calculate deep extrude distance (20% of Z)."""
        return self._dimensions[2] * 0.20

    def _calc_extrude_neg(self) -> float:
        """Calculate negative extrude (inward, -10% of Z)."""
        return -self._dimensions[2] * 0.10

    def _calc_scale_small(self) -> List[float]:
        """Calculate small scale (80% of each dimension)."""
        return [d * 0.8 for d in self._dimensions[:3]]

    def _calc_scale_tiny(self) -> List[float]:
        """Calculate tiny scale (50% of each dimension)."""
        return [d * 0.5 for d in self._dimensions[:3]]

    def _calc_offset(self) -> float:
        """Calculate offset (2% of min dim)."""
        return min(self._dimensions) * 0.02

    def _calc_thickness(self) -> float:
        """Calculate thickness (5% of Z)."""
        return self._dimensions[2] * 0.05

    def _calc_screen_depth(self) -> float:
        """Calculate screen depth for phone (50% of Z)."""
        return self._dimensions[2] * 0.50

    def _calc_screen_depth_neg(self) -> float:
        """Calculate negative screen depth (-50% of Z)."""
        return -self._dimensions[2] * 0.50

    def _calc_loop_pos(self) -> float:
        """Calculate loop cut position factor."""
        return 0.8

    def set_dimensions(self, dimensions: List[float]) -> None:
        """Set object dimensions for calculations.

        Args:
            dimensions: List of [width, height, depth] or [x, y, z].
        """
        if dimensions and len(dimensions) >= 3:
            self._dimensions = list(dimensions[:3])
        else:
            logger.warning(f"Invalid dimensions: {dimensions}")
            self._dimensions = None

    def get_dimensions(self) -> Optional[List[float]]:
        """Get current dimensions.

        Returns:
            Current dimensions or None.
        """
        return list(self._dimensions) if self._dimensions else None

    def clear_dimensions(self) -> None:
        """Clear stored dimensions."""
        self._dimensions = None

    def resolve(self, value: Any) -> Any:
        """Resolve a parameter value.

        Args:
            value: Parameter value (may be $AUTO_* reference).

        Returns:
            Resolved value. Returns original if not resolvable.
        """
        # Handle lists recursively
        if isinstance(value, list):
            return [self.resolve(v) for v in value]

        # Handle dicts recursively
        if isinstance(value, dict):
            return {k: self.resolve(v) for k, v in value.items()}

        # Non-string values pass through
        if not isinstance(value, str):
            return value

        # Not an AUTO param
        if not value.startswith("$AUTO_"):
            return value

        # No dimensions set
        if self._dimensions is None:
            logger.warning(f"Cannot resolve {value}: no dimensions set")
            return value

        # Look up and calculate
        if value in self._auto_params:
            try:
                calc_func = self._auto_params[value]["calculation"]
                result = calc_func()
                logger.debug(f"Resolved {value} -> {result}")
                return result
            except Exception as e:
                logger.error(f"Error resolving {value}: {e}")
                return value

        logger.warning(f"Unknown AUTO param: {value}")
        return value

    def resolve_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve all $AUTO_* parameters in a dictionary.

        Args:
            params: Dictionary of parameters.

        Returns:
            New dictionary with resolved values.
        """
        return {key: self.resolve(value) for key, value in params.items()}

    def get_available_params(self) -> List[Dict[str, str]]:
        """Get list of available $AUTO_* parameters.

        Returns:
            List of dicts with 'name' and 'description'.
        """
        return [
            {"name": name, "description": info["description"]}
            for name, info in self._auto_params.items()
        ]

    def is_auto_param(self, value: Any) -> bool:
        """Check if a value is an $AUTO_* parameter.

        Args:
            value: Value to check.

        Returns:
            True if value is an AUTO param string.
        """
        return isinstance(value, str) and value.startswith("$AUTO_")
