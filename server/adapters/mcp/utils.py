"""Shared utility functions for MCP adapter layer."""
import json
from typing import List, Optional, Union


def parse_coordinate(value: Union[str, List[float], None]) -> Optional[List[float]]:
    """
    Parse coordinate parameter that can be either a string or list.
    Handles MCP clients that send arrays as JSON strings.

    Args:
        value: Either a string like '[0.0, 0.0, 2.0]' or an actual list [0.0, 0.0, 2.0]

    Returns:
        Parsed list of floats or None if value is None

    Raises:
        ValueError: If the string cannot be parsed as a valid coordinate list

    Examples:
        >>> parse_coordinate('[0.0, 0.0, 2.0]')
        [0.0, 0.0, 2.0]
        >>> parse_coordinate([1, 2, 3])
        [1.0, 2.0, 3.0]
        >>> parse_coordinate(None)
        None
    """
    if value is None:
        return None

    if isinstance(value, str):
        try:
            # Parse JSON string to list
            parsed = json.loads(value)
            if not isinstance(parsed, list):
                raise ValueError(f"Expected a list, got {type(parsed).__name__}")
            return [float(x) for x in parsed]
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"Invalid coordinate format: {value}. "
                f"Expected a list like [0.0, 0.0, 0.0]. Error: {e}"
            )

    # Already a list, ensure all elements are floats
    return [float(x) for x in value]
