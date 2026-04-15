# Contributing to YOLO-Toys

Thanks for your interest in contributing! This document provides guidelines and workflows for contributing to the project.

## Table of Contents

- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Adding New Models](#adding-new-models)
- [Testing](#testing)

---

## Quick Start

```bash
# 1. Fork and clone
git clone https://github.com/YOUR-USERNAME/yolo-toys.git
cd yolo-toys

# 2. Create branch
git checkout -b feat/your-feature

# 3. Setup environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install

# 4. Make changes, then verify
make lint   # Run Ruff checks
make test   # Run pytest

# 5. Commit and push
git commit -m "feat: add your feature"
git push origin feat/your-feature

# 6. Open Pull Request on GitHub
```

---

## Development Setup

### Prerequisites

- Python 3.11+
- pip, venv
- (Optional) Docker for containerized testing

### Environment Variables

Create `.env` from the example for local development:

```bash
cp .env.example .env
```

Key variables for development:

| Variable | Default | Purpose |
|----------|---------|---------|
| `SKIP_WARMUP` | `false` | Set to `1` to skip model loading on startup |
| `MODEL_NAME` | `yolov8s.pt` | Default model for testing |
| `DEVICE` | `auto` | Force specific device if needed |

### IDE Setup

Recommended VS Code extensions:

- Python (Microsoft)
- Ruff (charliermarke.ruff)
- Pylance

---

## Code Style

We use **Ruff** for linting and formatting, configured in `pyproject.toml`.

### Key Rules

- **Line length:** 100 characters
- **Imports:** Sorted automatically by Ruff
- **Type hints:** Required for function signatures
- **Docstrings:** Preferred for public APIs

### Running Checks

```bash
make lint      # Check issues
make format    # Auto-fix issues
```

Or run Ruff directly:

```bash
ruff check app/ tests/
ruff format app/ tests/
```

---

## Commit Guidelines

We follow **Conventional Commits** for clear history:

### Format

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no code change |
| `refactor` | Code refactoring |
| `test` | Adding/updating tests |
| `chore` | Build, CI, dependencies |

### Examples

```bash
feat(handler): add support for SAM segment-anything model
fix(routes): handle empty file upload gracefully
docs(readme): update installation instructions
test(api): add WebSocket config update test
chore(docker): optimize multi-stage build layers
```

---

## Pull Request Process

### Before Submitting

- [ ] Code passes `make lint` with no errors
- [ ] All tests pass: `make test`
- [ ] New code has corresponding tests
- [ ] Documentation updated if needed
- [ ] Commit messages follow Conventional Commits

### PR Template

When you open a PR, include:

1. **Summary** — What and why
2. **Changes** — Key modifications
3. **Testing** — How you tested
4. **Screenshots** — If UI changes

### Review Process

1. Maintainers will review within a few days
2. Address feedback by pushing new commits
3. Once approved, a maintainer will merge

---

## Adding New Models

See `CLAUDE.md` for detailed architecture. Quick summary:

1. **Create Handler** — Extend `BaseHandler` in `app/handlers/`
2. **Implement Methods:**
   - `load(model_id)` → `(model, processor)`
   - `infer(model, processor, image, **params)` → `dict`
3. **Register Model:**
   - Add category to `ModelCategory` in `registry.py`
   - Add to `_CATEGORY_HANDLER_MAP`
   - Add metadata to `MODEL_REGISTRY`
4. **Add Tests** — Verify model loading and inference

---

## Testing

### Running Tests

```bash
make test
# or
python -m pytest -v
```

### Test Structure

```
tests/
├── __init__.py
└── test_api.py      # API + WebSocket tests
```

### Writing Tests

- Use `pytest.fixture` for setup
- Use `monkeypatch` for mocking `model_manager`
- Test both success and error cases

Example:

```python
def test_infer_endpoint(client: TestClient, image_bytes: bytes, mock_infer):
    files = {"file": ("test.png", image_bytes, "image/png")}
    r = client.post("/infer?model=yolov8n.pt", files=files)
    assert r.status_code == 200
    assert "detections" in r.json()
```

---

## Questions?

- Open a [GitHub Issue](https://github.com/LessUp/yolo-toys/issues) for bugs or features
- Check existing issues before creating new ones
- Provide reproduction steps and logs for bugs

Thank you for contributing! 🎉
