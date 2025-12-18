"""
Proportion Calculator.

Utility for calculating object proportions from dimensions.
"""

from typing import Dict, Any, List, Optional

from server.router.domain.entities.scene_context import ProportionInfo


def calculate_proportions(dimensions: List[float]) -> ProportionInfo:
    """Calculate proportions from object dimensions.

    Args:
        dimensions: Object dimensions [x, y, z].

    Returns:
        ProportionInfo with calculated proportions.
    """
    if not dimensions or len(dimensions) < 3:
        return ProportionInfo()

    x, y, z = dimensions[0], dimensions[1], dimensions[2]

    # Avoid division by zero
    x = max(x, 0.0001)
    y = max(y, 0.0001)
    z = max(z, 0.0001)

    min_dim = min(x, y, z)
    max_dim = max(x, y, z)

    # Calculate aspect ratios
    aspect_xy = x / y
    aspect_xz = x / z
    aspect_yz = y / z

    # Calculate flags
    is_flat = z < min(x, y) * 0.2
    is_tall = z > max(x, y) * 2
    is_wide = x > max(y, z) * 2
    is_cubic = max_dim / min_dim < 1.5

    # Determine dominant axis
    if x >= y and x >= z:
        dominant_axis = "x"
    elif y >= x and y >= z:
        dominant_axis = "y"
    else:
        dominant_axis = "z"

    # Calculate volume and surface area (box approximation)
    volume = x * y * z
    surface_area = 2 * (x * y + y * z + x * z)

    return ProportionInfo(
        aspect_xy=round(aspect_xy, 4),
        aspect_xz=round(aspect_xz, 4),
        aspect_yz=round(aspect_yz, 4),
        is_flat=is_flat,
        is_tall=is_tall,
        is_wide=is_wide,
        is_cubic=is_cubic,
        dominant_axis=dominant_axis,
        volume=round(volume, 6),
        surface_area=round(surface_area, 4),
    )


def get_proportion_summary(proportions: ProportionInfo) -> str:
    """Get human-readable summary of proportions.

    Args:
        proportions: ProportionInfo to summarize.

    Returns:
        String description of the shape.
    """
    descriptions = []

    if proportions.is_flat:
        descriptions.append("flat")
    if proportions.is_tall:
        descriptions.append("tall")
    if proportions.is_wide:
        descriptions.append("wide")
    if proportions.is_cubic:
        descriptions.append("cubic")

    if not descriptions:
        descriptions.append("irregular")

    return ", ".join(descriptions)


def is_phone_like_proportions(proportions: ProportionInfo, z_threshold: float = 0.15) -> bool:
    """Check if proportions match phone/tablet shape.

    Args:
        proportions: ProportionInfo to check.
        z_threshold: Maximum z dimension for "flat" phone.

    Returns:
        True if proportions match phone-like shape.
    """
    return (
        proportions.is_flat
        and 0.4 < proportions.aspect_xy < 0.7
        and proportions.volume < z_threshold * 2  # Roughly flat
    )


def is_tower_like_proportions(proportions: ProportionInfo) -> bool:
    """Check if proportions match tower/pillar shape.

    Args:
        proportions: ProportionInfo to check.

    Returns:
        True if proportions match tower-like shape.
    """
    return proportions.is_tall and proportions.aspect_xz < 0.5 and proportions.aspect_yz < 0.5


def is_table_like_proportions(proportions: ProportionInfo) -> bool:
    """Check if proportions match table/surface shape.

    Args:
        proportions: ProportionInfo to check.

    Returns:
        True if proportions match table-like shape.
    """
    return proportions.is_flat and not proportions.is_tall


def is_wheel_like_proportions(proportions: ProportionInfo) -> bool:
    """Check if proportions match wheel/disc shape.

    Args:
        proportions: ProportionInfo to check.

    Returns:
        True if proportions match wheel-like shape.
    """
    return proportions.is_flat and 0.9 < proportions.aspect_xy < 1.1


def get_dimensions_from_dict(data: Dict[str, Any]) -> Optional[List[float]]:
    """Extract dimensions from various data formats.

    Args:
        data: Dictionary that may contain dimensions.

    Returns:
        List of [x, y, z] dimensions or None.
    """
    # Try direct dimensions key
    if "dimensions" in data:
        dims = data["dimensions"]
        if isinstance(dims, (list, tuple)) and len(dims) >= 3:
            return [float(dims[0]), float(dims[1]), float(dims[2])]
        if isinstance(dims, dict):
            return [
                float(dims.get("x", 1.0)),
                float(dims.get("y", 1.0)),
                float(dims.get("z", 1.0)),
            ]

    # Try x, y, z keys directly
    if "x" in data and "y" in data and "z" in data:
        return [float(data["x"]), float(data["y"]), float(data["z"])]

    # Try size key
    if "size" in data:
        size = data["size"]
        if isinstance(size, (list, tuple)) and len(size) >= 3:
            return [float(size[0]), float(size[1]), float(size[2])]

    return None
