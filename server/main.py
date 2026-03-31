# SPDX-FileCopyrightText: 2024-2026 Patryk Ciechański
# SPDX-License-Identifier: Apache-2.0

"""
Blender AI MCP Server
Author: Patryk Ciechański (https://github.com/PatrykIti)
"""

import logging
import os

from server.infrastructure.config import get_config
from server.infrastructure.telemetry import initialize_telemetry_from_config

# Get log level from env, default to INFO
log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_name, logging.INFO)

logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

if __name__ == "__main__":
    config = get_config()
    initialize_telemetry_from_config(config)

    from server.adapters.mcp.server import run

    run()
