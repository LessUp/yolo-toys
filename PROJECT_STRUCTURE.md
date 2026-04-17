# Project Structure

This document describes the organization of the YOLO-Toys codebase.

## Root Directory

The root directory contains essential project files and configuration:

```
yolo-toys/
├── README.md                  # Project overview (English)
├── README.zh-CN.md           # Project overview (Chinese)
├── LICENSE                   # MIT License
├── SECURITY.md               # Security policy
├── CODE_OF_CONDUCT.md        # Community guidelines
├── CONTRIBUTING.md           # Contribution guide
├── AGENTS.md                 # AI assistant instructions
├── CLAUDE.md                 # Claude-specific context
├── Makefile                  # Build automation
├── pyproject.toml            # Python project configuration
├── docker-compose.yml        # Docker Compose (root level)
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development dependencies
├── .editorconfig             # Editor configuration
├── .pre-commit-config.yaml   # Pre-commit hooks
├── .gitignore                # Git ignore rules
│
# GitHub Pages / Jekyll (must be at root)
├── _config.yml               # Jekyll configuration
├── index.md                  # GitHub Pages entry
├── 404.md                    # 404 page
├── _includes/                # Jekyll includes
├── _layouts/                 # Jekyll layouts
├── assets/                   # Jekyll assets (CSS)
│
# Project directories (see below)
├── app/                      # Backend application
├── frontend/                 # Frontend code
├── config/                   # Configuration examples
├── changelog/                # Version history
├── docs/                     # Documentation
├── deployments/              # Deployment configs
├── scripts/                  # Utility scripts
├── specs/                    # Specifications (RFCs)
└── tests/                    # Test suite
```

## Directory Descriptions

### `app/` - Backend Application

Core Python application code.

```
app/
├── __init__.py           # Package initialization
├── main.py               # FastAPI entry point
├── config.py             # Settings management
├── routes.py             # API endpoints
├── schemas.py            # Pydantic models
├── model_manager.py      # Model lifecycle management
├── metrics.py            # Prometheus metrics
├── middleware.py         # HTTP middleware
└── handlers/             # Model handler implementations
    ├── base.py           # Base handler class
    ├── registry.py       # Handler registry
    ├── yolo_handler.py   # YOLO models
    ├── hf_handler.py     # Hugging Face models
    └── blip_handler.py   # BLIP models
```

### `frontend/` - Web Frontend

Static frontend files served by FastAPI.

```
frontend/
├── index.html            # Main page
├── app.js                # Application logic
├── style.css             # Stylesheet
└── js/                   # Additional JS modules
```

### `config/` - Configuration Examples

Environment configuration templates.

```
config/
├── .env.example          # Base configuration template
├── .env.development      # Development environment
└── .env.production       # Production environment
```

### `deployments/` - Deployment Configurations

All deployment-related files.

```
deployments/
├── README.md             # Deployment guide
├── docker/               # Docker configurations
│   ├── Dockerfile        # Standard CPU image
│   ├── Dockerfile.cuda   # NVIDIA GPU image
│   ├── docker-compose.yml
│   └── .dockerignore
└── monitoring/           # Monitoring stack
    ├── prometheus/
    └── grafana/
```

### `docs/` - Documentation

Project documentation content (not GitHub Pages).

```
docs/
├── README.md             # Documentation index
├── api/                  # API documentation
├── architecture/         # Architecture docs
├── deployment/           # Deployment guides
├── getting-started/      # Quick start guides
├── guides/               # How-to guides
└── reference/            # Reference materials
```

### `specs/` - Specifications

Project specifications and RFCs.

```
specs/
├── api/                  # API specifications (OpenAPI)
├── db/                   # Database schemas
├── product/              # Product requirements
├── rfc/                  # RFC documents
└── testing/              # Test specifications
```

### `scripts/` - Utility Scripts

Development and utility scripts.

```
scripts/
└── dev.sh                # Development helper script
```

### `tests/` - Test Suite

Test files and fixtures.

```
tests/
├── __init__.py
├── conftest.py           # Pytest fixtures
└── test_api.py           # API tests
```

### `changelog/` - Version History

Detailed change logs for each version.

```
changelog/
├── index.md              # Changelog index
├── CHANGELOG.md          # Latest changes
├── v3.1.0.md
├── v3.0.0.md
└── archive/              # Older changelogs
```

## Important Notes

### GitHub Pages Files at Root

The following files must remain at the root for GitHub Pages to work:

- `_config.yml` - Jekyll configuration
- `index.md` - Site entry point
- `404.md` - Error page
- `_includes/` - Template includes
- `_layouts/` - Page layouts
- `assets/` - Static assets

### Docker Context

When building Docker images from the project root:

```bash
# Standard build (CPU)
docker build -f deployments/docker/Dockerfile -t yolo-toys .

# CUDA build (GPU)
docker build -f deployments/docker/Dockerfile.cuda -t yolo-toys:cuda .
```

### Docker Compose

The root `docker-compose.yml` is kept for convenience:

```bash
# Quick start
docker compose up

# With monitoring
docker compose --profile monitoring up
```

## Migration Notes

Previous directory layout had Docker files at root. They have been moved to:

- `Dockerfile` → `deployments/docker/Dockerfile`
- `Dockerfile.cuda` → `deployments/docker/Dockerfile.cuda`
- `.dockerignore` → `deployments/docker/.dockerignore`
- `.env.example` → `config/.env.example`

Old paths are no longer valid. Update your workflows accordingly.
