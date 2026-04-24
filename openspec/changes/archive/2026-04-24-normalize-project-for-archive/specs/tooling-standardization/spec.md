## ADDED Requirements

### Requirement: Repository-scoped AI tooling guidance SHALL be explicit
The repository SHALL define project-scoped guidance for Claude, Copilot, Codex, OpenCode, and related assistant workflows so tool behavior stays aligned with YOLO-Toys priorities.

#### Scenario: Assistant initializes in the repository
- **WHEN** an assistant starts working in the YOLO-Toys repository
- **THEN** repository-scoped guidance clearly describes expected workflows, constraints, and division of responsibilities between tools

### Requirement: Machine-global tooling adjustments SHALL be bounded
The project SHALL describe which machine-global tool changes are required, optional, or unsupported when standardizing the user's local environment for this repository.

#### Scenario: Applying global configuration
- **WHEN** the user or an agent configures machine-global settings for this repository's tooling stack
- **THEN** each global change is documented with intent, scope, and a clear boundary between project necessity and personal preference

### Requirement: Recommended LSP and editor integration SHALL be defined
The project SHALL specify a preferred Python LSP and editor integration baseline that is compatible with the repository's type-checking, formatting, and linting expectations.

#### Scenario: Setting up a supported editor
- **WHEN** a contributor configures an editor for YOLO-Toys
- **THEN** the repository provides a recommended LSP, formatter, linter, and related editor settings that work together without overlapping responsibilities

### Requirement: MCP usage SHALL be conservative and justified
The project SHALL define a minimal MCP policy that prefers lower-overhead skills or CLI workflows unless MCP brings clear project-specific value.

#### Scenario: Evaluating a new MCP integration
- **WHEN** a contributor considers adding or enabling an MCP integration for this repository
- **THEN** the documented policy requires weighing context cost, maintenance burden, and unique capability before adopting it
