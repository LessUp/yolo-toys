## ADDED Requirements

### Requirement: Repository health validation SHALL be reproducible
The project MUST provide a reproducible repository-health validation path that covers engineering entry points, linting behavior, tests, and other archive-readiness checks required by the normalized workflow.

#### Scenario: Running the repository validation flow
- **WHEN** a contributor follows the documented repository validation commands
- **THEN** the commands execute in a predictable order with explicit prerequisites and clearly reveal whether the repository is ready to merge or finalize

### Requirement: Finalization changes SHALL include a bug sweep
The project MUST require a final bug sweep for repository-wide normalization changes before they are considered complete.

#### Scenario: Closing a large cleanup change
- **WHEN** a repository-wide cleanup or archive-readiness change reaches its final phase
- **THEN** the workflow includes an explicit bug sweep that checks remaining correctness issues across code, docs, automation, and public project surfaces
