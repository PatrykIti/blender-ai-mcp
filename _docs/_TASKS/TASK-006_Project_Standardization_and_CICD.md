---
type: task
id: TASK-006_Project_Standardization_and_CICD
title: Project Standardization and CI/CD Setup
status: done
priority: high
assignee: unassigned
depends_on: TASK-005_Dockerize_Server
---

# 🎯 Objective
Prepare the repository for a professional, public open-source release. This includes setting up CI/CD pipelines, standardizing documentation (English only), creating contribution guidelines, and issue templates.

# 📋 Scope of Work

## 1. Documentation Standardization (English)
- **Translate `_docs/MVP_EXTENDED.md`**: Convert content to English and save as `ARCHITECTURE.md` in the root (or `_docs/ARCHITECTURE.md`).
- **Update `README.md`**:
  - Professional project description.
  - Badges (CI status, Python version, License, Stars).
  - "Star History" chart section.
  - Clear usage instructions for MCP Clients (Cline, Claude Code) with Docker.
- **Create `CONTRIBUTING.md`**:
  - Guidelines based on our current workflow (Clean Architecture, Task-based development).
  - Code style (Python, Pydantic).
  - Pull Request process.

## 2. GitHub Templates (`.github/`)
- **Issue Templates**:
  - `bug_report.md`: Structured bug reporting.
  - `feature_request.md`: Proposal for new tools/features.
- **Pull Request Template**:
  - `PULL_REQUEST_TEMPLATE.md`: Checklist for Clean Architecture compliance, tests, and documentation updates.

## 3. CI/CD Pipeline (`.github/workflows/`)
- **Workflow: `release.yml`**:
  - Trigger: Push to `main` (or manual dispatch).
  - **Job 1: Test**: Run unit tests.
  - **Job 2: Build Addon**: Generate `blender_ai_mcp.zip`.
  - **Job 3: Release**:
    - Use `semantic-release` (or similar) to tag version.
    - Create GitHub Release.
    - Upload `blender_ai_mcp.zip` as a release asset.
  - **Job 4: Docker Push**:
    - Build Docker image.
    - Push to GHCR (`ghcr.io/OWNER/blender-ai-mcp:latest` & `:tag`).

# ✅ Acceptance Criteria
- All documentation is in professional English.
- `README.md` is comprehensive and user-friendly.
- `CONTRIBUTING.md` clearly explains the architectural rules.
- GitHub Issue/PR templates are in place.
- CI/CD pipeline successfully builds, tests, and publishes artifacts (Zip & Docker) on merge to main.