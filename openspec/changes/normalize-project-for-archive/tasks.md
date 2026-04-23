## 1. OpenSpec foundation

- [x] 1.1 Audit the current OpenSpec layout, legacy `specs/` drift, and repository structure conflicts that must be normalized first
- [x] 1.2 Archive the completed `improve-test-coverage` change and ensure the new normalization change becomes the active source of truth
- [x] 1.3 Update repository structure documentation so it reflects the actual `openspec/`-driven layout and removes obsolete structural claims

## 2. Baseline developer experience

- [x] 2.1 Refactor Makefile and related command entry points to separate non-mutating checks from mutating fix/format behavior
- [x] 2.2 Repair test and setup command assumptions so local validation works with explicit interpreter and dependency requirements
- [x] 2.3 Re-run the normalized repository validation flow and fix baseline issues discovered by the updated commands

## 3. Governance and workflow documents

- [x] 3.1 Rewrite `AGENTS.md` into a project-specific collaboration guide aligned with YOLO-Toys architecture and the final maintenance goal
- [x] 3.2 Rewrite `CLAUDE.md` so it captures repository-specific workflow, review checkpoints, and OpenSpec-first execution rules
- [x] 3.3 Add concise workflow guidance that defines propose/apply/review/archive usage, autopilot defaults, and limited `/fleet` usage

## 4. Documentation and repository structure cleanup

- [x] 4.1 Remove or consolidate stale, redundant, and low-value docs across `README*`, `docs/`, and `changelog/`
- [x] 4.2 Rebuild the documentation hierarchy so README, docs, changelog, and governance files each have a distinct role
- [x] 4.3 Update issue, PR, and other repository templates so they match the normalized workflow and reduced-maintenance posture

## 5. Engineering and automation normalization

- [x] 5.1 Simplify `pyproject.toml`, pre-commit hooks, env templates, and related engineering config around archive-ready quality gates
- [x] 5.2 Refactor GitHub Actions workflows to keep only high-signal CI, Pages, release, and security automation
- [x] 5.3 Verify the normalized automation paths trigger only on meaningful changes and do not perform low-value work

## 6. Public packaging and site redesign

- [x] 6.1 Redesign GitHub Pages into a landing surface with a clear value proposition, fast-start paths, and curated documentation links
- [x] 6.2 Align README messaging and site messaging so users see one coherent project story across repository surfaces
- [x] 6.3 Use `gh` to update repository description, homepage URL, and topic tags to match the finalized public positioning

## 7. AI tooling and local environment standardization

- [x] 7.1 Add repository-scoped Copilot, Claude, Codex, and OpenCode guidance/configuration where project-level settings are beneficial
- [x] 7.2 Standardize the preferred LSP and editor baseline for the Python stack and add project-scoped editor settings if appropriate
- [x] 7.3 Audit and document the minimal MCP policy, then apply only the justified machine-global tool changes needed for this repository

## 8. Final sweep and archive readiness

- [x] 8.1 Run a final repository-wide bug sweep covering code, docs, workflows, Pages, and metadata after the structural cleanup lands
- [x] 8.2 Close any residual inconsistencies between specs, implementation, documentation, and automation
- [x] 8.3 Confirm the repository meets the explicit archive-readiness criteria and record the final validation outcome
