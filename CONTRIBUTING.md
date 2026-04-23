# Contributing to YOLO-Toys

Thanks for contributing. This repository is **OpenSpec-driven** and currently optimized for **high-quality finalization**, not broad feature expansion.

## Working principles

- Prefer finishing and simplifying over adding new scope.
- Keep docs, workflows, and public project surfaces coherent.
- Avoid unstable tests, duplicate docs, and noisy automation.
- For non-trivial work, start from OpenSpec instead of editing first and documenting later.

## Setup

```bash
git clone https://github.com/LessUp/yolo-toys.git
cd yolo-toys
bash scripts/dev.sh setup
. .venv/bin/activate
```

## Required validation commands

```bash
make lint     # non-mutating checks
make format   # apply Ruff fixes
make hooks    # full pre-commit run
make test     # pytest + coverage
```

## OpenSpec workflow

Use this flow for any non-trivial change to code, docs, workflows, or repository structure:

1. `/opsx:explore` — investigate and clarify scope
2. `/opsx:propose` — create the change proposal/design/tasks
3. `/opsx:apply` — implement the change tasks
4. `/review` — run a review at major phase boundaries
5. `/opsx:archive` — archive the completed change

### When to use `/review`

Run a review after major phases such as:

- baseline/tooling changes
- workflow or CI refactors
- large doc reductions
- GitHub Pages/public packaging changes

## Change guidelines

### Runtime and tests

- Prefer mocked handler/model loading in tests.
- Keep normal test runs independent of network/model downloads.
- Add or update tests when behavior changes.

### Documentation

- `README*` is the repository entry point.
- `docs/` is long-form usage/reference material.
- GitHub Pages root files are for landing/navigation.
- `changelog/` is release history only.

Do not mirror the same text across all four surfaces.

### Automation

- Keep workflow triggers narrow and high-signal.
- Avoid adding automation that creates more noise than protection.

## Pull requests

- Keep PRs phase-oriented and reviewable.
- Explain the problem, the meaningful changes, and how you validated them.
- Update OpenSpec artifacts and relevant canonical docs together when the workflow requires it.

## AI-assisted contribution

- Repository guidance lives in `AGENTS.md`, `CLAUDE.md`, and `.github/copilot-instructions.md`.
- Default to single-agent autopilot or focused manual edits.
- Use subagents selectively for audits and low-coupling parallel work.
- Avoid `/fleet` unless the task clearly justifies the extra cost.
