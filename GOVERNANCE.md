# NetworkForge Governance

This document outlines the governance model for the NetworkForge open-source project.

## Project Structure
NetworkForge is a community-driven project with a BDFL (Benevolent Dictator for Life) model in its early stages, transitioning towards a steering committee model as the community grows.

## Roles and Responsibilities

### Core Maintainers
Core Maintainers have push access to the repository, merge PRs, and define the project roadmap.
- To become a maintainer, a contributor must submit at least 5 substantial PRs and be nominated by an existing maintainer.

### Release Manager
The Release Manager is responsible for:
- Cutting new releases via GitHub Actions.
- Reviewing the `CHANGELOG.md`.
- Managing security advisories.
- *Currently rotating weekly among Core Maintainers.*

### Contributors
Anyone who opens a PR, files an issue, or helps with documentation. We value all contributions equally.

## RFC Process
For significant architectural changes (e.g., adding a new LLM provider, changing the database schema), contributors must open an Issue tagged with `[RFC]`.
1. The community has 7 days to discuss the RFC.
2. A Core Maintainer must approve the RFC before implementation begins.

## Security Disclosures
Please do not open public issues for security vulnerabilities. Review our `SECURITY.md` for disclosure policies.
