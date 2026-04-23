# Project Structure

This document describes the current, canonical layout of the YOLO-Toys repository.

## Repository Top Level

```text
yolo-toys/
├── app/                      # FastAPI application and model runtime
├── config/                   # Environment templates
├── deployments/              # Docker and monitoring assets
├── docs/                     # User and operator documentation content
├── frontend/                 # Static frontend served by the backend
├── openspec/                 # OpenSpec source of truth for behavior and changes
├── scripts/                  # Helper scripts
├── tests/                    # Test suite
├── .claude/                  # Project-scoped Claude/OpenSpec commands and skills
├── .github/                  # GitHub workflows and templates
├── _config.yml               # GitHub Pages / Jekyll configuration
├── _data/                    # GitHub Pages navigation and site data
├── _includes/                # GitHub Pages partial templates
├── _layouts/                 # GitHub Pages layouts
├── assets/                   # Shared site assets
├── changelog/                # Release notes and version history
├── 404.md                    # GitHub Pages 404 page
├── index.md                  # GitHub Pages landing page
├── AGENTS.md                 # Repository guidance for AI coding agents
├── CLAUDE.md                 # Claude-specific repository guidance
├── Makefile                  # Developer entry points
├── pyproject.toml            # Python project and tool configuration
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Development dependencies
└── README.md                 # Primary repository entry point
```

## Key Directories

### `app/`

Application runtime, request handling, configuration, middleware, metrics, model management, and model handlers.

```text
app/
├── api/                      # Route modules and request utilities
├── handlers/                 # Model handler implementations
├── config.py                 # Settings management
├── main.py                   # FastAPI entry point
├── metrics.py                # Prometheus metrics
├── middleware.py             # HTTP middleware
├── model_manager.py          # Model cache and inference coordination
├── routes.py                 # Router composition
└── schemas.py                # Response/request schemas
```

### `openspec/`

OpenSpec is the authoritative planning and behavior layer for non-trivial repository changes.

```text
openspec/
├── config.yaml               # Project-wide OpenSpec configuration
├── specs/                    # Current behavior and repository standards
│   ├── api/
│   ├── domain/
│   ├── product/
│   └── testing/
└── changes/                  # Proposed, active, and completed change artifacts
```

### `docs/`

Long-form documentation for setup, architecture, deployment, and reference material. This directory feeds the documentation section of the site but is not the same thing as the GitHub Pages landing experience.

### `changelog/`

Version and release history. This directory should contain release-oriented information only, not general documentation.

### GitHub Pages root files

The published site is assembled from root-level Jekyll files plus selected project content:

- `_config.yml`
- `index.md`
- `404.md`
- `_data/`
- `_includes/`
- `_layouts/`
- `assets/`

### `.claude/`

Repository-scoped Claude/OpenSpec workflow assets:

- `commands/opsx/*` for OpenSpec command entry points
- `skills/openspec-*` for propose/explore/apply/archive workflows

## Important Structural Rules

1. `openspec/` replaces the legacy `specs/`-style planning model; new planning artifacts belong under OpenSpec.
2. README, `docs/`, `changelog/`, and GitHub Pages each serve different purposes and should not mirror the same content verbatim.
3. Deployment assets belong under `deployments/`, not the repository root, unless a root convenience wrapper is intentionally kept.
4. New repository-wide process or governance changes should update both OpenSpec artifacts and the relevant canonical docs.

## Common Paths

```bash
# Run the application
uvicorn app.main:app --reload

# CPU Docker build
docker build -f deployments/docker/Dockerfile -t yolo-toys .

# CUDA Docker build
docker build -f deployments/docker/Dockerfile.cuda -t yolo-toys:cuda .
```
