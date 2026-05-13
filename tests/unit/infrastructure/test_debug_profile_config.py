"""Tests for BLENDER_AI_DEBUG config parsing."""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from server.infrastructure.config import Config


def test_config_parses_named_debug_scopes() -> None:
    config = Config.model_validate({"BLENDER_AI_DEBUG": "vision,tools"})

    assert config.BLENDER_AI_DEBUG == frozenset({"vision", "tools"})


def test_config_parses_off_as_explicit_empty_selector() -> None:
    config = Config.model_validate({"BLENDER_AI_DEBUG": "off"})

    assert config.BLENDER_AI_DEBUG == frozenset()


def test_config_normalizes_all_over_specific_scopes() -> None:
    config = Config.model_validate({"BLENDER_AI_DEBUG": "all,vision"})

    assert config.BLENDER_AI_DEBUG == frozenset({"all"})


def test_config_rejects_invalid_debug_scope_name() -> None:
    with pytest.raises(ValidationError, match="Unknown BLENDER_AI_DEBUG scope"):
        Config.model_validate({"BLENDER_AI_DEBUG": "vison"})


def test_config_rejects_duplicate_debug_scope_name() -> None:
    with pytest.raises(ValidationError, match="duplicate scope names"):
        Config.model_validate({"BLENDER_AI_DEBUG": "router,router"})
