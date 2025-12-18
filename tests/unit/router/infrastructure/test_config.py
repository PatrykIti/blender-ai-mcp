"""
Unit tests for Router Configuration.

Tests for RouterConfig dataclass.
"""

import pytest
from server.router.infrastructure.config import RouterConfig


class TestRouterConfigDefaults:
    """Test default configuration values."""

    def test_default_correction_settings(self):
        """Test default correction settings."""
        config = RouterConfig()

        assert config.auto_mode_switch is True
        assert config.auto_selection is True
        assert config.clamp_parameters is True

    def test_default_override_settings(self):
        """Test default override settings."""
        config = RouterConfig()

        assert config.enable_overrides is True
        assert config.enable_workflow_expansion is True

    def test_default_firewall_settings(self):
        """Test default firewall settings."""
        config = RouterConfig()

        assert config.block_invalid_operations is True
        assert config.auto_fix_mode_violations is True

    def test_default_thresholds(self):
        """Test default threshold values."""
        config = RouterConfig()

        assert config.embedding_threshold == 0.40
        assert config.bevel_max_ratio == 0.5
        assert config.subdivide_max_cuts == 6

    def test_default_advanced_settings(self):
        """Test default advanced settings."""
        config = RouterConfig()

        assert config.cache_scene_context is True
        assert config.cache_ttl_seconds == 1.0
        assert config.max_workflow_steps == 20
        assert config.log_decisions is True


class TestRouterConfigCustom:
    """Test custom configuration values."""

    def test_custom_correction_settings(self):
        """Test custom correction settings."""
        config = RouterConfig(
            auto_mode_switch=False,
            auto_selection=False,
            clamp_parameters=False,
        )

        assert config.auto_mode_switch is False
        assert config.auto_selection is False
        assert config.clamp_parameters is False

    def test_custom_thresholds(self):
        """Test custom threshold values."""
        config = RouterConfig(
            embedding_threshold=0.75,
            bevel_max_ratio=0.3,
            subdivide_max_cuts=4,
        )

        assert config.embedding_threshold == 0.75
        assert config.bevel_max_ratio == 0.3
        assert config.subdivide_max_cuts == 4

    def test_partial_custom_settings(self):
        """Test mixing custom and default settings."""
        config = RouterConfig(
            auto_mode_switch=False,
            embedding_threshold=0.60,
        )

        # Custom values
        assert config.auto_mode_switch is False
        assert config.embedding_threshold == 0.60

        # Default values preserved
        assert config.auto_selection is True
        assert config.clamp_parameters is True
        assert config.enable_overrides is True


class TestRouterConfigSerialization:
    """Test configuration serialization."""

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = RouterConfig()
        data = config.to_dict()

        assert isinstance(data, dict)
        assert data["auto_mode_switch"] is True
        assert data["auto_selection"] is True
        assert data["clamp_parameters"] is True
        assert data["enable_overrides"] is True
        assert data["enable_workflow_expansion"] is True
        assert data["block_invalid_operations"] is True
        assert data["auto_fix_mode_violations"] is True
        assert data["embedding_threshold"] == 0.40
        assert data["bevel_max_ratio"] == 0.5
        assert data["subdivide_max_cuts"] == 6
        assert data["cache_scene_context"] is True
        assert data["cache_ttl_seconds"] == 1.0
        assert data["max_workflow_steps"] == 20
        assert data["log_decisions"] is True

    def test_to_dict_custom_values(self):
        """Test to_dict with custom values."""
        config = RouterConfig(
            auto_mode_switch=False,
            embedding_threshold=0.80,
        )
        data = config.to_dict()

        assert data["auto_mode_switch"] is False
        assert data["embedding_threshold"] == 0.80

    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "auto_mode_switch": False,
            "auto_selection": False,
            "embedding_threshold": 0.75,
        }
        config = RouterConfig.from_dict(data)

        assert config.auto_mode_switch is False
        assert config.auto_selection is False
        assert config.embedding_threshold == 0.75
        # Default values for non-specified fields
        assert config.clamp_parameters is True

    def test_from_dict_ignores_unknown_keys(self):
        """Test that from_dict ignores unknown keys."""
        data = {
            "auto_mode_switch": False,
            "unknown_key": "should be ignored",
            "another_unknown": 123,
        }
        config = RouterConfig.from_dict(data)

        assert config.auto_mode_switch is False
        assert not hasattr(config, "unknown_key")
        assert not hasattr(config, "another_unknown")

    def test_roundtrip_serialization(self):
        """Test config survives to_dict -> from_dict roundtrip."""
        original = RouterConfig(
            auto_mode_switch=False,
            auto_selection=False,
            clamp_parameters=False,
            enable_overrides=False,
            embedding_threshold=0.65,
            bevel_max_ratio=0.4,
            subdivide_max_cuts=3,
        )

        data = original.to_dict()
        restored = RouterConfig.from_dict(data)

        assert restored.auto_mode_switch == original.auto_mode_switch
        assert restored.auto_selection == original.auto_selection
        assert restored.clamp_parameters == original.clamp_parameters
        assert restored.enable_overrides == original.enable_overrides
        assert restored.embedding_threshold == original.embedding_threshold
        assert restored.bevel_max_ratio == original.bevel_max_ratio
        assert restored.subdivide_max_cuts == original.subdivide_max_cuts


class TestRouterConfigValidation:
    """Test configuration value validation."""

    def test_threshold_bounds(self):
        """Test that thresholds can be set to edge values."""
        config_min = RouterConfig(embedding_threshold=0.0)
        config_max = RouterConfig(embedding_threshold=1.0)

        assert config_min.embedding_threshold == 0.0
        assert config_max.embedding_threshold == 1.0

    def test_subdivide_cuts_positive(self):
        """Test subdivide cuts can be set to positive values."""
        config = RouterConfig(subdivide_max_cuts=1)
        assert config.subdivide_max_cuts == 1

        config = RouterConfig(subdivide_max_cuts=10)
        assert config.subdivide_max_cuts == 10

    def test_cache_ttl_values(self):
        """Test cache TTL can be set to various values."""
        config = RouterConfig(cache_ttl_seconds=0.5)
        assert config.cache_ttl_seconds == 0.5

        config = RouterConfig(cache_ttl_seconds=10.0)
        assert config.cache_ttl_seconds == 10.0
