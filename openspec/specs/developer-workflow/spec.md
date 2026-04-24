## ADDED Requirements

### Requirement: Non-trivial work SHALL follow an OpenSpec-first lifecycle
The repository SHALL require non-trivial structural, documentation, workflow, or code changes to begin with OpenSpec exploration or proposal artifacts before implementation proceeds.

#### Scenario: Starting a repository-wide change
- **WHEN** a contributor or agent begins a non-trivial repository change
- **THEN** an OpenSpec change exists that defines the change scope, design intent, and implementation tasks before broad code or documentation edits are made

### Requirement: Review checkpoints SHALL be part of the delivery flow
The repository SHALL define when `/review`, subagents, and phase-level validation are expected during delivery so large cleanups are not merged without structured review.

#### Scenario: Completing a major implementation phase
- **WHEN** a major phase such as workflow refactoring, documentation reduction, or Pages redesign is completed
- **THEN** the documented workflow includes a review checkpoint before the change is treated as ready to finalize

### Requirement: Automation modes SHALL have explicit boundaries
The repository SHALL document how autopilot, long-running single-agent execution, and exceptional `/fleet` usage are selected for this project.

#### Scenario: Choosing an execution mode
- **WHEN** an agent plans implementation for this repository
- **THEN** the project guidance prefers long-running single-agent autopilot by default and reserves `/fleet` for clearly parallel, low-coupling work only

### Requirement: Developer commands SHALL distinguish check and fix behavior
The repository SHALL provide developer commands whose names and behavior clearly separate non-mutating validation from mutating repair actions.

#### Scenario: Running repository validation locally
- **WHEN** a contributor runs a command intended for validation
- **THEN** the command does not silently rewrite repository files and any mutating fix command is exposed under a separate, explicit entry point
