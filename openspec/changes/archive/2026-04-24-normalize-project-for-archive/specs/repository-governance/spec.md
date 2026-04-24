## ADDED Requirements

### Requirement: Repository structure SHALL be canonical
The repository SHALL maintain one canonical directory structure definition that matches the actual project layout and explicitly identifies deprecated or transitional areas.

#### Scenario: Structure documentation matches the repository
- **WHEN** a contributor or agent inspects the documented project structure
- **THEN** the documented directories, responsibilities, and migration notes match the files and folders that actually exist in the repository

### Requirement: Governance documents SHALL be project-specific
The repository SHALL provide governance documents that encode YOLO-Toys-specific rules for architecture, documentation, and AI-assisted contribution instead of generic boilerplate.

#### Scenario: Assistant reads governance files
- **WHEN** an AI assistant or contributor opens governance files such as `AGENTS.md` or `CLAUDE.md`
- **THEN** the files describe YOLO-Toys-specific constraints, workflows, and decision boundaries needed to work on this repository

### Requirement: Archive-readiness criteria SHALL be explicit
The repository SHALL define explicit criteria for when the project is considered structurally complete and ready for low-maintenance archival mode.

#### Scenario: Final readiness review
- **WHEN** the normalization change reaches its final verification stage
- **THEN** the repository can be evaluated against a documented archive-readiness checklist covering structure, documentation, automation, metadata, and unresolved bugs
