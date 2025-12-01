"""
Router Configuration.

Configuration dataclass for router behavior settings.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class RouterConfig:
    """Configuration for Router Supervisor behavior.

    Attributes:
        auto_mode_switch: Automatically switch Blender mode if needed.
        auto_selection: Automatically select geometry if tool requires it.
        clamp_parameters: Clamp parameter values to valid ranges.
        enable_overrides: Enable tool override rules.
        enable_workflow_expansion: Enable workflow expansion for patterns.
        block_invalid_operations: Block operations that would fail.
        auto_fix_mode_violations: Auto-fix mode violations instead of blocking.
        embedding_threshold: Minimum confidence for intent classification.
        bevel_max_ratio: Maximum bevel width as ratio of smallest dimension.
        subdivide_max_cuts: Maximum subdivision cuts allowed.
    """

    # Correction settings
    auto_mode_switch: bool = True
    auto_selection: bool = True
    clamp_parameters: bool = True

    # Override settings
    enable_overrides: bool = True
    enable_workflow_expansion: bool = True

    # Firewall settings
    block_invalid_operations: bool = True
    auto_fix_mode_violations: bool = True

    # Thresholds
    embedding_threshold: float = 0.40
    bevel_max_ratio: float = 0.5
    subdivide_max_cuts: int = 6

    # Advanced settings
    cache_scene_context: bool = True
    cache_ttl_seconds: float = 1.0
    max_workflow_steps: int = 20
    log_decisions: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "auto_mode_switch": self.auto_mode_switch,
            "auto_selection": self.auto_selection,
            "clamp_parameters": self.clamp_parameters,
            "enable_overrides": self.enable_overrides,
            "enable_workflow_expansion": self.enable_workflow_expansion,
            "block_invalid_operations": self.block_invalid_operations,
            "auto_fix_mode_violations": self.auto_fix_mode_violations,
            "embedding_threshold": self.embedding_threshold,
            "bevel_max_ratio": self.bevel_max_ratio,
            "subdivide_max_cuts": self.subdivide_max_cuts,
            "cache_scene_context": self.cache_scene_context,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "max_workflow_steps": self.max_workflow_steps,
            "log_decisions": self.log_decisions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RouterConfig":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})
