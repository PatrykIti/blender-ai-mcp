# 10. Project Standardization and CI/CD

**Date:** 2025-11-22  
**Version:** 0.1.9  
**Tasks:** TASK-006_Project_Standardization_and_CICD

## 🚀 Key Changes

### Documentation
- **Language**: Switched to English in main files (`README.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`).
- **ARCHITECTURE.md**: Detailed technical description (Clean Architecture, RPC Protocol) translated from previous notes.
- **CONTRIBUTING.md**: New contributor guide emphasizing task workflow and architecture.
- **README.md**: Professional look, CI statuses, Docker instructions.

### Automation (CI/CD)
- **GitHub Actions (`.github/workflows/release.yml`)**:
  - Automatic testing (`unittest`).
  - Building Addon artifact (`blender_ai_mcp.zip`).
  - Semantic Release: Automatic versioning, tagging, and GitHub Release creation.
  - Docker: Build and push image to GHCR (GitHub Container Registry).
- **Templates**: Added Issue (`Bug`, `Feature`) and Pull Request templates.

The project is now fully prepared for publication as a professional Open Source tool.
