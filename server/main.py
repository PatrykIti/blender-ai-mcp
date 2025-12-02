"""
Blender AI MCP Server
Author: Patryk Ciechański (https://github.com/PatrykIti)
"""
import logging
import os
from server.adapters.mcp.server import run

# Get log level from env, default to INFO
log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_name, logging.INFO)

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    run()
