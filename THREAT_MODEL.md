# Threat Model - ResumeMatch AI

## 1. System Description
ResumeMatch AI is a web platform for analyzing CVs against Job Descriptions using AI.
- **Frontend**: Next.js, deployed on Vercel/similar.
- **Backend**: FastAPI (Python), deployed via Docker Compose.
- **Database**: PostgreSQL (relational data, user accounts, analysis results).
- **Cache & Queue**: Redis (Celery broker, WebSocket tickets).
- **Workers**: Celery (Background AI processing).
- **External Services**: LLMs via Groq / Ollama, Telegram (Notifications), Sentry (Error tracking).

## 2. Trust Boundaries
- **Public Network**: Unauthenticated users interacting with frontend/backend.
- **Authenticated Zone**: Users with valid JWTs accessing their data.
- **Internal Network**: Docker network communicating between FastAPI, PostgreSQL, Redis, and Celery.
- **Third-Party Boundary**: Outbound connections to LLM providers (Groq) and notification APIs (Telegram).

## 3. Data Flow & Assets
- **Assets**: User emails, hashed passwords, CV files (PII), Job Descriptions, API keys.
- **Data Flow**:
  1. User uploads CV & JD.
  2. Backend securely stores data and queues Celery task.
  3. Worker pulls task, anonymizes PII (if applicable), sends to LLM.
  4. LLM returns match score and feedback.
  5. Worker saves result, notifies user via WebSocket.

## 4. Threat Identification (STRIDE)

| Threat Type | Description | Mitigation Strategy |
|-------------|-------------|---------------------|
| **Spoofing** | Attacker impersonates a user via stolen tokens. | JWT with short TTL, HttpOnly Secure cookies, Refresh Token rotation with token family tracking. API keys with strict scopes. |
| **Tampering**| Attacker modifies API requests or DB directly. | Strong input validation using Pydantic. Use SQLAlchemy/asyncpg parameterized queries to prevent SQLi. Internal DB not exposed to public internet. |
| **Repudiation** | User denies performing an action (e.g. deleting account). | Audit logs for critical actions. Retain minimal logs to comply with GDPR. |
| **Information Disclosure** | PII leakage via Sentry, LLM, or unauthorized API access. | Implement PII scrubbing before LLM API calls and Sentry logging. Enforce strict row-level security / endpoint ownership checks. TLS/HTTPS enforced. |
| **Denial of Service** | Abuse of AI generation endpoint to incur high costs / CPU load. | Enforce rate limiting via `slowapi` on endpoints. Limit CV/JD payload sizes. Queue system (Celery) prevents main API loop blocking. |
| **Elevation of Privilege** | Normal user accesses admin endpoints or other users' data. | RBAC implementation (`is_superuser`). Strong dependency checks (Dependabot, pip-audit, Trivy). |

## 5. Known Risks & Acceptances
- **LLM Hallucination/Injection**: Mitigated by system prompt constraints, but full prevention is impossible.
- **Local/Self-hosted Security**: If deployed locally, security depends on host configuration. Docker isolation helps but is not foolproof if host is compromised.
