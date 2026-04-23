# CLAUDE.md

## What matters in this repository

YOLO-Toys already has the runtime features it needs. The active priority is to finish the repository cleanly: stabilize the baseline, reduce drift, simplify automation, improve the public presentation, and leave behind a low-maintenance codebase.

## Claude operating rules

### 1. Start from OpenSpec

- Read `openspec/specs/` before changing behavior, workflow, or documentation structure.
- Prefer `/opsx:explore` for investigation, `/opsx:propose` for new change setup, and `/opsx:apply` for implementation.
- Keep completed changes archived so the active change list stays clean.

### 2. Respect the current repository roles

- `app/` is the runtime.
- `openspec/` is the source of truth for non-trivial work.
- `docs/` is long-form documentation.
- root Pages files are for landing/navigation, not full README duplication.
- `changelog/` is only for release history.

### 3. Use the normalized command surface

```bash
bash scripts/dev.sh setup
. .venv/bin/activate
make lint
make format
make hooks
make test
```

- `make lint` must stay non-mutating.
- `make format` is where automatic fixes belong.
- `make hooks` is the full pre-commit gate.

### 4. Keep tests and automation stable

- Do not add tests that require real model downloads for routine validation.
- Prefer monkeypatching or mocking handler/model loading paths.
- Keep workflow triggers narrow and meaningful.
- Preserve high-signal checks; remove low-value automation noise.

### 5. Review and autopilot strategy

- Use `/review` after major phases, not after every tiny edit.
- Default to single-agent autopilot for implementation.
- Use subagents when auditing large docs/workflow surfaces.
- Avoid `/fleet` unless the work is clearly parallel, low-coupling, and worth the extra consumption.

### 6. Tooling stance

- Repository-scoped instructions/config should define the project contract.
- Machine-global tooling changes are allowed for this project, but keep them minimal and reversible.
- Preferred Python tooling baseline: Ruff + a type-aware Python LSP (Pyright/BasedPyright family).
- Prefer CLI/skills over MCP when they provide the same value with less context overhead.
