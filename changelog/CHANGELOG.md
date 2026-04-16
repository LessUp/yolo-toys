# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Placeholder for upcoming features

---

## [3.1.0] - 2026-04-16

### 📝 Documentation System Refactor

This release focuses on comprehensive documentation improvements and bilingual support.

### Added
- Professional bilingual documentation system (English/Chinese)
- Restructured `docs/` directory with organized categories:
  - `getting-started/` — Installation and quick start guides
  - `api/` — REST API and WebSocket protocol documentation
  - `architecture/` — System design and handler pattern documentation
  - `deployment/` — Docker and production deployment guides
  - `guides/` — Development tutorials (adding custom models)
  - `reference/` — Quick reference materials (models, FAQ)
- Standardized changelog following Keep a Changelog format
- Complete API reference with request/response examples
- Architecture documentation explaining design patterns (Strategy, Registry, Template Method)
- Model compatibility matrix with performance benchmarks
- Comprehensive FAQ covering installation, performance, and troubleshooting

### Changed
- Documentation navigation optimized with clear categorization
- Cross-language linking between English and Chinese documents
- Enhanced code examples in all documentation

### Documentation
- All documentation now available in both English and Chinese
- README.md and README.zh-CN.md cross-referenced
- Changelog follows Keep a Changelog specification

---

## [3.0.0] - 2026-02-13

### 🏗️ Architecture Refactor

Major architectural overhaul with strategy pattern implementation and improved maintainability.

### Added
- **Strategy Pattern Architecture**: New `app/handlers/` module
  - `base.py` — BaseHandler abstract class with unified interface
  - `registry.py` — HandlerRegistry factory and MODEL_REGISTRY metadata
  - `yolo_handler.py` — YOLO detection/segmentation/pose handler
  - `hf_handler.py` — DETR / OWL-ViT / Grounding DINO handlers
  - `blip_handler.py` — BLIP Caption / VQA handlers
- **Pydantic Settings**: Unified environment configuration in `app/config.py`
  - Type validation and `.env` file support
  - Derived properties for computed settings
- **Enhanced Testing**: Test cases increased from 6 to 16+
  - WebSocket connection/inference/config update tests
  - Model info endpoint tests (404/200)
  - Boundary input tests (invalid content-type, empty files)
  - HandlerRegistry unit tests
  - AppSettings configuration tests
- **Modern FastAPI Patterns**
  - Lifespan context manager replacing deprecated `@app.on_event`
  - Route extraction to dedicated `routes.py`
  - Structured logging replacing print statements

### Changed
- `model_manager.py` simplified from 814 lines to ~100 lines
- `main.py` reduced from 410 lines to 91 lines
- Frontend URL building extracted to common functions
- `.gitignore` and `.dockerignore` enhanced
- `pyproject.toml` updated with `[project]` metadata

### Removed
- Deprecated `on_event("startup")` usage
- Redundant code in model manager

---

## [2.0.0] - 2025-11-25

### 🎯 Multi-Model System

Comprehensive support for multiple AI models with dynamic switching.

### Added
- **Multi-Model Support System**
  - YOLO Detection: YOLOv8 n/s/m/l/x
  - YOLO Segmentation: YOLOv8-seg series
  - YOLO Pose: YOLOv8-pose series
  - Transformer: DETR ResNet-50/101
  - Open Vocabulary: OWL-ViT zero-shot detection
  - Multimodal: BLIP Caption and Visual QA
- **New API Endpoints**
  - `GET /models` — List all available models by category
  - `GET /models/{model_id}` — Get model details
  - `POST /caption` — Image captioning
  - `POST /vqa` — Visual question answering
  - WebSocket configuration updates at runtime
- **Frontend UI Overhaul**
  - Modern dark/light theme design
  - Model category tabs with quick switching
  - Toast notification system
  - Real-time performance overlay
  - Settings persistence in localStorage

### Changed
- Model management unified through ModelManager
- API response format standardized
- Frontend refactored with ES Modules

---

## [1.0.0] - 2025-02-13

### 🚀 Project Launch

Initial project infrastructure and basic YOLO functionality.

### Added
- FastAPI backend with REST endpoints
- YOLOv8 object detection support
- WebSocket streaming for real-time detection
- Basic HTML/CSS/JS frontend
- Docker support
- GitHub Actions CI/CD

---

## Release Link Format

- [3.1.0]: https://github.com/LessUp/yolo-toys/releases/tag/v3.1.0
- [3.0.0]: https://github.com/LessUp/yolo-toys/releases/tag/v3.0.0
- [2.0.0]: https://github.com/LessUp/yolo-toys/releases/tag/v2.0.0
- [1.0.0]: https://github.com/LessUp/yolo-toys/releases/tag/v1.0.0
