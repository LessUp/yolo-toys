## ADDED Requirements

### Requirement: GitHub Pages SHALL act as a landing surface
The published site SHALL introduce the project with a clear value proposition, fast entry paths, and curated links into deeper documentation instead of duplicating the entire README verbatim.

#### Scenario: New visitor lands on the site
- **WHEN** a user opens the GitHub Pages homepage
- **THEN** the page explains what YOLO-Toys is, why it matters, how to try it quickly, and where to go next for architecture or operational details

### Requirement: Public repository metadata SHALL be aligned
The GitHub repository description, homepage URL, and topic tags SHALL be aligned with the repository README and GitHub Pages positioning.

#### Scenario: Viewing the repository summary card
- **WHEN** a user sees the repository on GitHub or in search results
- **THEN** the description, homepage, and topics accurately reflect the project's final positioning and point to the published site

### Requirement: Public content surfaces SHALL have distinct roles
The repository SHALL define distinct jobs for README, GitHub Pages, docs, changelog, and governance files so the same content is not duplicated across all surfaces.

#### Scenario: Finding project information
- **WHEN** a contributor or user navigates between README, site pages, docs, and changelog
- **THEN** each surface provides a different layer of information and links to the correct deeper source instead of restating the same content
