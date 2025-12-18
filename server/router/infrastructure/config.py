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
        workflow_similarity_threshold: Minimum similarity for semantic workflow match.
        generalization_threshold: Minimum similarity for workflow generalization.
        enable_generalization: Enable workflow generalization for unknown objects.
        use_ensemble_matching: Enable ensemble matching (TASK-053).
        keyword_weight: Weight for keyword matcher in ensemble (TASK-053).
        semantic_weight: Weight for semantic matcher in ensemble (TASK-053).
        pattern_weight: Weight for pattern matcher in ensemble (TASK-053).
        pattern_boost_factor: Boost multiplier when pattern matcher fires (TASK-053).
        composition_threshold: Threshold for multi-workflow composition mode (TASK-053).
        enable_composition_mode: Enable composition mode (future feature, TASK-053).
        ensemble_high_threshold: Minimum score for HIGH confidence (TASK-053).
        ensemble_medium_threshold: Minimum score for MEDIUM confidence (TASK-053).
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

    # Semantic workflow matching thresholds (TASK-046)
    workflow_similarity_threshold: float = 0.5  # Min for direct semantic match
    generalization_threshold: float = 0.3  # Min for generalization
    enable_generalization: bool = True  # Enable workflow generalization

    # Workflow adaptation settings (TASK-051)
    enable_workflow_adaptation: bool = True  # Enable confidence-based workflow adaptation
    adaptation_semantic_threshold: float = 0.6  # Min similarity for optional step inclusion

    # Ensemble matching settings (TASK-053)
    use_ensemble_matching: bool = True  # Enable ensemble matching
    keyword_weight: float = 0.40  # Weight for keyword matcher
    semantic_weight: float = 0.40  # Weight for semantic matcher
    pattern_weight: float = 0.15  # Weight for pattern matcher
    pattern_boost_factor: float = 1.3  # Boost when pattern matcher fires
    composition_threshold: float = 0.15  # Threshold for multi-workflow mode
    enable_composition_mode: bool = False  # Future feature
    ensemble_high_threshold: float = 0.7  # Score >= this → HIGH confidence
    ensemble_medium_threshold: float = 0.4  # Score >= this → MEDIUM confidence

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
            "workflow_similarity_threshold": self.workflow_similarity_threshold,
            "generalization_threshold": self.generalization_threshold,
            "enable_generalization": self.enable_generalization,
            "enable_workflow_adaptation": self.enable_workflow_adaptation,
            "adaptation_semantic_threshold": self.adaptation_semantic_threshold,
            "use_ensemble_matching": self.use_ensemble_matching,
            "keyword_weight": self.keyword_weight,
            "semantic_weight": self.semantic_weight,
            "pattern_weight": self.pattern_weight,
            "pattern_boost_factor": self.pattern_boost_factor,
            "composition_threshold": self.composition_threshold,
            "enable_composition_mode": self.enable_composition_mode,
            "ensemble_high_threshold": self.ensemble_high_threshold,
            "ensemble_medium_threshold": self.ensemble_medium_threshold,
            "cache_scene_context": self.cache_scene_context,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "max_workflow_steps": self.max_workflow_steps,
            "log_decisions": self.log_decisions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RouterConfig":
        """Create config from dictionary."""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})
