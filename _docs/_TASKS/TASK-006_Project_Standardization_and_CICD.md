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
- **Translate `_docs/MVP_EXTENDED.md`**: Convert content to English and save as `ARCHITECTURE.md`.
- **Update `README.md`**: Professional description, badges, usage instructions.
- **Create `CONTRIBUTING.md`**: Guidelines on Clean Architecture.

## 2. GitHub Templates (`.github/`)
- Issue Templates (`bug_report.md`, `feature_request.md`).
- Pull Request Template.

## 3. CI/CD Pipeline (`.github/workflows/`)
- **Workflow: `release.yml`**:
  - Trigger: Push to `main`.
  - **Jobs**: Test, Build Addon Zip, Semantic Release, Docker Push.

# ✅ Acceptance Criteria
- All documentation in English.
- CI/CD pipeline fully functional.
