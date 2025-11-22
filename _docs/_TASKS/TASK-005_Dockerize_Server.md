---
type: task
id: TASK-005_Dockerize_Server
title: MCP Server Containerization (Docker)
status: done
priority: medium
assignee: unassigned
depends_on: TASK-004_Modeling_Tools
---

# 🎯 Objective
Create a Docker image for the MCP server to facilitate distribution and running in an isolated environment.

# 📋 Scope of Work

1. **Dockerfile**
   - Base image: `python:3.10-slim`.
   - Install Poetry and dependencies.
   - Copy source code.

2. **Networking**
   - Server in container must connect to Blender on host.
   - Use `host.docker.internal`.
   - Parameterize RPC host via env vars (`BLENDER_RPC_HOST`).

3. **Config Update (`server/infrastructure/config.py`)**
   - Implement env var loading.

4. **Documentation**
   - Build and run instructions in `README.md`.

# ✅ Acceptance Criteria
- Can build image: `docker build`.
- Can run container connecting to Blender on host.
- MCP tools work from container.
