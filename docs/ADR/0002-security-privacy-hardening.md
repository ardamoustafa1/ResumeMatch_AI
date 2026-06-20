# ADR 0002: Security and Privacy Hardening (Phase 2)

## Status
Accepted

## Context
As ResumeMatch AI handles PII (Personally Identifiable Information) such as resumes, names, emails, and job application history, we needed to significantly harden our security and privacy posture before launching to production. The Phase 1 MVP focused on functional completion, but left several security and privacy gaps, including incomplete data export/deletion, broad API key permissions, weak file upload checks, and lack of automated security scanning in CI.

## Decision
We implemented a comprehensive security and privacy hardening plan, which includes:

1.  **GDPR/CCPA Compliance**: 
    - Implemented a secure `GET /api/v1/auth/export` endpoint for users to download all their data in JSON format.
    - Implemented `DELETE /api/v1/auth/me` to completely remove a user and cascade delete all their related analyses, api keys, and tokens.
2.  **API Key Scope Enforcement**: 
    - Migrated from path-based implicit checks to strict `fastapi.security.SecurityScopes`. API Keys now require explicit declaration (e.g., `Scope.EXTENSION`) to access any endpoint, preventing key misuse on unrelated routes.
3.  **File Upload Security**:
    - Added strict validation to block polyglot, malicious, and excessively large files during the PDF upload process.
    - Integrated `pip-audit`, `bandit` (SAST), `trivy` (container scanning), and CodeQL into the GitHub Actions CI pipeline.
4.  **Extension Hardening (Manifest V3)**:
    - Replaced the ephemeral `sessionStorage` with `chrome.storage.local`.
    - Narrowed `host_permissions` in `manifest.json` from the overly broad `*/*` to specifically target `https://www.linkedin.com/jobs/*` and our API host.
5.  **Observability & E2E Testing**:
    - Introduced a Prometheus `/metrics` endpoint to monitor database connection pools and HTTP request latency.
    - Added `user_id` and `request_id` to loguru context variables for structured logging across all system boundaries.
    - Bootstrapped Playwright for end-to-end frontend tests and integrated `@axe-core/playwright` for automated accessibility audits.

## Consequences
- **Positive**: The platform is now secure and compliant with standard data protection regulations. The CI pipeline will automatically reject PRs with known vulnerabilities or linting errors. 
- **Negative**: The addition of Playwright and several security scanners increases the CI execution time slightly. Developers must now be careful to assign scopes when creating new API endpoints if they expect the extension to consume them.
