# Copilot instructions for YOLO-Toys

- Treat this repository as **finalization-oriented**: prefer coherence, cleanup, and correctness over new feature expansion.
- Read `openspec/specs/` before making non-trivial changes.
- Use the active change in `openspec/changes/` as the source of implementation tasks.
- Keep `README*`, `docs/`, GitHub Pages root files, and `changelog/` serving different purposes; do not duplicate the same content across them.
- Keep tests deterministic. Prefer mocks over real model downloads or network-dependent validation.
- Use these commands as the canonical local workflow:
  - `bash scripts/dev.sh setup`
  - `. .venv/bin/activate`
  - `make lint`
  - `make format`
  - `make hooks`
  - `make test`
- `make lint` is non-mutating. `make format` is the fix path.
- Prefer smaller, high-signal workflow changes over broad CI expansion.
- When changing public positioning (README, Pages, docs), also check whether GitHub description/homepage/topics need to stay aligned.
