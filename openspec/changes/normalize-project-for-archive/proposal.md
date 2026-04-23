## Why

YOLO-Toys has working product code, but the repository has drifted away from a clean OpenSpec-driven, archive-ready state. Documentation, workflow automation, repository structure, GitHub Pages, and AI tooling guidance have accumulated inconsistencies that make the project harder to finish confidently and harder for new users to understand quickly.

This change is needed now to turn the repository into a stable final-state release candidate: easier to validate, easier to present on GitHub, and easier to hand off to future low-maintenance use without continuing structural decay.

## What Changes

- Create a repository-wide normalization pass focused on archive readiness rather than feature expansion.
- Make OpenSpec the authoritative change-management workflow for repository evolution, including proposal, review, apply, and archive conventions.
- Simplify repository structure, remove stale or redundant documentation, and rewrite governance documents so they are project-specific and actionable.
- Redesign GitHub Pages and repository metadata so the public project presentation is coherent across GitHub, README, and Pages.
- Streamline engineering configuration, hooks, and GitHub Actions so quality gates remain high-signal while reducing noisy or low-value automation.
- Standardize AI-assisted development guidance for Claude, Copilot, Codex, OpenCode, LSP, MCP, review flow, and autopilot usage.
- Fix baseline developer-experience issues discovered during audit, including inconsistent command semantics and broken environment assumptions.

## Capabilities

### New Capabilities
- `repository-governance`: Defines repository structure rules, documentation boundaries, archive-readiness criteria, and project-specific governance documents.
- `developer-workflow`: Defines the OpenSpec-first development lifecycle, review checkpoints, automation boundaries, hook behavior, and AI-assisted collaboration flow.
- `project-packaging`: Defines GitHub Pages positioning, GitHub repository metadata, and release/presentation alignment for the final project state.
- `tooling-standardization`: Defines supported local tooling, LSP/editor expectations, and the boundary between repo-scoped and machine-global AI/tool configuration.

### Modified Capabilities
- `product`: Refines how the project is positioned and communicated to users through the repository and site experience.
- `testing`: Changes acceptance expectations for repository health so baseline validation covers engineering-entry correctness, workflow sanity, and archive-readiness checks in addition to runtime behavior.

## Impact

- Affected areas include `openspec/`, root governance documents, `README*`, `docs/`, `changelog/`, `_config.yml`, Pages layouts/assets, `.github/` workflows/templates, `Makefile`, `pyproject.toml`, pre-commit configuration, editor/tooling config, and selected local/global AI tool settings.
- Public-facing GitHub metadata will be updated through `gh`.
- No new product runtime features are planned; impact is concentrated on quality, structure, process, presentation, and correctness of the existing project.
