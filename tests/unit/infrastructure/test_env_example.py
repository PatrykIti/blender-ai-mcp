"""Coverage for the tracked .env.example configuration template."""

from __future__ import annotations

import re
from pathlib import Path

from server.infrastructure.config import Config

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_env_example_lists_every_config_field_once():
    """The checked-in .env.example should stay in sync with Config fields."""

    text = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")
    listed = re.findall(r"^([A-Z0-9_]+)=", text, flags=re.MULTILINE)

    assert listed
    assert len(listed) == len(set(listed))
    assert set(listed) == set(Config.model_fields)


def test_env_example_includes_transport_and_vision_guidance():
    """The example file should document the currently important runtime knobs."""

    text = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")

    for expected in (
        "MCP_TRANSPORT_MODE=stdio",
        "MCP_HTTP_HOST=127.0.0.1",
        "MCP_STREAMABLE_HTTP_PATH=/mcp",
        "VISION_PROVIDER=transformers_local",
        "VISION_EXTERNAL_PROVIDER=generic",
    ):
        assert expected in text


def test_config_env_file_allows_launcher_only_provider_aliases(tmp_path):
    """A quick-launch .env may include secrets and launcher-only variables."""

    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "OPENROUTER_API_KEY=test-secret",
                "REFERENCE_CLASSIFIER_AUTO_START=true",
                "SEGMENTATION_SIDECAR_AUTO_START=true",
                "LOCALIZATION_SIDECAR_AUTO_START=true",
                "VISION_ENABLED=true",
                "VISION_PROVIDER=openai_compatible_external",
                "VISION_EXTERNAL_PROVIDER=openrouter",
                "VISION_OPENROUTER_API_KEY_ENV=OPENROUTER_API_KEY",
                "VISION_OPENROUTER_MODEL=x-ai/grok-4.3",
                "VISION_SEGMENTATION_ENABLED=true",
                "VISION_LOCALIZATION_ENABLED=true",
            ]
        ),
        encoding="utf-8",
    )

    config = Config(_env_file=env_file)

    assert config.VISION_ENABLED is True
    assert config.VISION_PROVIDER == "openai_compatible_external"
    assert config.VISION_EXTERNAL_PROVIDER == "openrouter"
    assert config.VISION_OPENROUTER_API_KEY_ENV == "OPENROUTER_API_KEY"
    assert config.VISION_SEGMENTATION_ENABLED is True
    assert config.VISION_LOCALIZATION_ENABLED is True
