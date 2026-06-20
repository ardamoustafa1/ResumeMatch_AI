# Security Policy

## Supported Versions

We currently provide security updates for the `main` branch. Older tagged releases will receive backported patches only for critical severity issues.

| Version | Supported          |
| ------- | ------------------ |
| `main`  | :white_check_mark: |
| `< 1.0` | :x:                |

## Reporting a Vulnerability

Security is a core principle of ResumeMatch AI. If you discover a vulnerability, we would like to know about it so we can take steps to address it as quickly as possible.

**Do not open a public issue.**

Please report security issues by emailing [security@resumematch.ai](mailto:security@resumematch.ai). We will acknowledge receipt of your vulnerability report within 48 hours and strive to send you regular updates about our progress.

When reporting a vulnerability, please include:
- A detailed description of the vulnerability.
- Steps to reproduce the issue.
- Potential impact and an estimated CVSS score (if possible).
- Any proof of concept (PoC) code or screenshots.

## Data Privacy & Telemetry
ResumeMatch AI is designed as a **local-first** application. By default, your CV data, job descriptions, and generated outreach drafts are processed solely within your own hosted environment (or configured APIs) and are never sent to external telemetry servers. We take proactive measures to strip PII before external API calls if configured to do so.
