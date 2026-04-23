## Context

YOLO-Toys already has substantial product functionality, but the repository no longer has a single authoritative structure for how the project should be developed, validated, and presented. OpenSpec exists but has not fully absorbed repository governance. Public-facing assets span README, GitHub Pages, GitHub metadata, docs, and changelog, yet these surfaces are only partially aligned. Engineering entry points also have drift: quality commands mix checking and mutation, local assumptions are not encoded clearly, and workflow automation is heavier than what a near-finished project needs.

This change is cross-cutting because it touches repository structure, documentation, workflows, public packaging, and AI tooling conventions at the same time. The goal is not to introduce more moving parts, but to remove ambiguity so the repository can enter a stable, low-maintenance final state.

Constraints:

- The worktree already contains user changes, so implementation must avoid blindly reverting or overwriting unrelated edits.
- The project is intended to be finished and stabilized, not expanded with new end-user runtime features.
- OpenSpec should become the single source of truth for non-trivial future work.
- Tooling guidance must cover both repository-scoped configuration and the user's machine-global configuration, but changes should remain low-risk and reversible.

## Goals / Non-Goals

**Goals:**

- Make OpenSpec the canonical workflow for future repository changes.
- Normalize repository structure and remove stale, redundant, or low-value project documentation.
- Redesign governance documents so they are specific to YOLO-Toys and useful during final maintenance.
- Reduce workflow noise while keeping high-signal quality gates intact.
- Align GitHub Pages, GitHub metadata, README, and docs into one coherent project story.
- Define a practical AI-assisted development model for Claude, Copilot, Codex, OpenCode, review, autopilot, LSP, and MCP usage.
- Fix baseline developer-experience issues surfaced by the audit.

**Non-Goals:**

- Adding new model families, endpoints, or user-facing runtime capabilities.
- Re-architecting the inference engine beyond what is required for repository correctness or consistency.
- Supporting every possible editor or AI tool equally; the design will recommend a primary path and document alternatives.
- Preserving all existing documentation purely for completeness if it no longer adds value.

## Decisions

### Decision: Use a dedicated OpenSpec normalization change as the root of all follow-up work

This repository-wide cleanup is too broad to execute as ad hoc edits. A dedicated change creates a stable contract for specs, design, tasks, review checkpoints, and completion criteria.

**Alternatives considered**
- Continue making direct cleanup commits without a change: faster initially, but would repeat the drift problem.
- Reuse `improve-test-coverage`: rejected because that change is already complete and has a different purpose.

### Decision: Treat repository governance as first-class spec surface

The current specs focus mostly on runtime product behavior. This change adds repository governance, workflow, packaging, and tooling capabilities so future repository-quality work is specifiable and reviewable.

**Alternatives considered**
- Keep governance only in markdown docs: rejected because it would remain advisory instead of enforceable.
- Overload existing runtime specs: rejected because it would blur product behavior with repository operations.

### Decision: Separate public surfaces by job instead of mirroring the same content everywhere

README, GitHub Pages, docs, changelog, and governance docs should each have one clear purpose. The implementation should remove duplicate explanations and instead build a content hierarchy:

- README: concise repository entry point
- GitHub Pages: attractive landing and orientation surface
- docs/: operational and reference documentation
- changelog/: curated release history only
- governance docs: contributor and AI workflow rules

**Alternatives considered**
- Keep README as the master source and mirror it into Pages/docs: rejected because it creates low-value duplication.
- Preserve all current docs and only restyle them: rejected because the core problem is information architecture, not cosmetics.

### Decision: Redesign quality commands around explicit semantics

Repository entry points should distinguish checking from mutation:

- check/lint commands: non-mutating, CI-safe
- fix/format commands: mutating, intentional
- test commands: explicit interpreter/dependency assumptions

This keeps local behavior predictable and makes CI failures easier to reason about.

**Alternatives considered**
- Keep `pre-commit run --all-files` as the main lint command: rejected because it silently mutates files during a supposed check.
- Let CI remain stricter than local commands: rejected because it hides breakage until push time.

### Decision: Prefer minimal, high-signal automation for an archive-bound repository

GitHub Actions should be refactored around a narrower set of valuable workflows. CI should focus on reproducible correctness. Pages should build only when relevant surfaces change. Release automation should match the project's final maintenance posture instead of maximizing activity.

**Alternatives considered**
- Preserve the broad current workflow matrix: rejected because it increases maintenance cost and noise.
- Remove most automation entirely: rejected because the repository still needs a trustworthy finishing gate.

### Decision: Standardize around repo-scoped guidance plus carefully bounded machine-global setup

Repository-scoped configuration should hold the canonical project rules. Machine-global tool configuration should be adjusted only where repo-scoped settings are insufficient, and every global adjustment should be documented with clear intent and rollback guidance.

**Alternatives considered**
- Repository-only setup: rejected because the user explicitly wants current machine-global tooling standardized too.
- Aggressive tool-by-tool global customization without project contract: rejected because it would create opaque local state.

### Decision: Favor a small tooling baseline

For Python development, the primary path should center on Ruff plus a type-aware Python LSP (Pyright/BasedPyright). MCP usage should be conservative; use CLI and skills first when they provide lower-context, lower-overhead outcomes.

**Alternatives considered**
- Add many MCP servers and editor integrations: rejected because context and maintenance cost are too high for the current goal.
- Avoid formal LSP/editor guidance: rejected because tooling inconsistency is one of the current sources of drift.

## Risks / Trade-offs

- **[Risk] Broad cleanup collides with existing uncommitted work** → Mitigation: sequence work from structure/specs outward, inspect diffs carefully, and avoid reverting unrelated edits.
- **[Risk] Documentation reduction removes useful edge-case information** → Mitigation: keep only content with a clear audience and link deep details from the right primary surface instead of duplicating them.
- **[Risk] Workflow simplification accidentally removes a needed safety check** → Mitigation: preserve high-signal validation gates and revalidate the final automation set against actual repository needs.
- **[Risk] Machine-global tool changes become environment-specific** → Mitigation: document assumptions, keep changes minimal, and prefer reversible configuration steps.
- **[Risk] New governance specs become too abstract to apply** → Mitigation: write requirements in operational, testable language with concrete scenarios tied to repository actions.

## Migration Plan

1. Finalize the new OpenSpec change artifacts.
2. Archive the completed historical change to reduce ambiguity.
3. Stabilize engineering entry points and repository structure before mass documentation edits.
4. Rewrite governance docs and then align tooling/workflow configs to those rules.
5. Redesign public surfaces and sync GitHub metadata after the content hierarchy is stable.
6. Run a final bug sweep and repository-health pass before declaring archive readiness.

Rollback will be handled as ordinary Git history rollback for repository files and as documented manual reversal steps for any machine-global tooling changes.

## Open Questions

- Which machine-global tool surfaces are currently present on the user's system and safe to standardize automatically?
- Whether GitHub repository settings beyond description/homepage/topics should be changed in this pass or documented for manual follow-up.
