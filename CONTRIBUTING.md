# Contributing

Thanks for your interest in contributing!

## Quick Start
1. Fork and clone the repo.
2. Create a new branch: `git checkout -b feat/your-change`.
3. Create a virtualenv and install deps:
   ```bash
   python -m venv .venv
   # Linux/macOS: source .venv/bin/activate
   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   pre-commit install
   ```
4. Run checks locally:
   ```bash
   pre-commit run --all-files   # Ruff lint + format
   python -m pytest             # Tests
   ```
5. Commit, push, and open a Pull Request.

## Guidelines
- Keep PRs small and focused. Include description, screenshots if UI changes.
- Include tests when possible. Avoid large binary files in git.
- Code style: Ruff (lint + format), configured in `pyproject.toml`.
- Prefer Conventional Commits style for commit messages (e.g. `feat: ...`, `fix: ...`).

## Issues
- Use GitHub Issues for bugs/features. Provide steps to reproduce and logs.
