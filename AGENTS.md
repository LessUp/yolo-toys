# AGENTS.md

## Mission

YOLO-Toys is in **finalization mode**. Prioritize correctness, coherence, and reduction over feature expansion. Prefer removing drift, redundant docs, noisy automation, and unstable tests rather than adding new surface area.

## Non-negotiables

1. **OpenSpec first** for any non-trivial change.
2. **Keep public surfaces distinct**:
   - `README*`: repository entry point
   - `docs/`: operational/reference docs
   - GitHub Pages root files: landing and navigation
   - `changelog/`: release history only
3. **Keep tests deterministic**. Normal test runs must not depend on model downloads, network access, or interactive steps.
4. **Keep automation high-signal**. CI, Pages, release, and security workflows should exist only when they provide clear ongoing value.
5. **Treat repo-scoped config as canonical**. Any machine-global tool changes must be minimal, reversible, and documented.

## Repository map

- `app/`: FastAPI runtime, routes, model manager, middleware, metrics
- `app/handlers/`: handler strategy implementations
- `tests/`: pytest suite
- `openspec/specs/`: current behavior and repository standards
- `openspec/changes/`: active change artifacts
- `.claude/`: project-scoped OpenSpec commands and skills
- `.github/`: workflows, templates, Copilot instructions
- `docs/`: long-form docs
- root Jekyll files (`index.md`, `_config.yml`, `_layouts/`, `_includes/`, `_data/`, `assets/`): GitHub Pages

## Required workflow

1. Read the relevant `openspec/specs/` files first.
2. For exploration or scoping, use `/opsx:explore`.
3. For new work, create or update a change with `/opsx:propose`.
4. Implement from the active change with `/opsx:apply`.
5. Use `/review` at phase boundaries such as:
   - baseline/tooling
   - governance/docs
   - workflows/automation
   - Pages/public packaging
6. Archive completed changes promptly with `/opsx:archive`.

## Preferred command surface

```bash
bash scripts/dev.sh setup     # create .venv and install runtime + dev deps
. .venv/bin/activate
make lint                     # non-mutating checks
make format                   # mutating Ruff fixes
make hooks                    # full pre-commit run
make test                     # pytest with coverage
```

## Implementation bias

- Favor focused refactors over broad rewrites unless a document or config is fundamentally unsalvageable.
- When touching workflows or docs, align the surrounding entry points too; do not leave half-migrated guidance behind.
- When fixing tests, prefer mocks/stubs over real model loads.
- When updating Pages or README messaging, keep GitHub repo metadata in sync.

## AI collaboration rules

- Default to a **single long-running agent/autopilot path** for implementation.
- Use subagents for audits, comparisons, and low-coupling parallel work.
- Avoid `/fleet` unless the task is clearly batchable and worth the quota cost.
- Do not treat AGENTS.md or CLAUDE.md as marketing docs; they are execution docs.
