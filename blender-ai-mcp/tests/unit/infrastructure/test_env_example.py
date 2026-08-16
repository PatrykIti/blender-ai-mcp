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
