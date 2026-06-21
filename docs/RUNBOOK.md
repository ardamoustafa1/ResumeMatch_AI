# Production runbook

## Triage order

1. Confirm `/api/v1/health/live` and `/api/v1/health/ready`.
2. Check API 5xx rate, latency, worker count, queue depth, and database pool use.
3. Correlate logs using `X-Request-ID`.
4. Pause deployments while an incident is active.
5. Preserve evidence without copying CV or job-description content into tickets.

## Queue outage

- Verify Redis health and Celery worker registration.
- Restart only the unhealthy worker after checking for an active deployment.
- Pending jobs are idempotent and protected by a Redis lock.
- If the broker is unavailable, the API marks newly created jobs as failed.

## LLM provider outage

- Confirm whether Groq and the configured Ollama fallback are both unavailable.
- Disable the failing provider or switch the deployment to the approved fallback.
- Never log raw prompts or provider responses containing user data.

## Database saturation

- Check active connections and long-running queries.
- Scale API workers only after confirming the database connection budget.
- Do not raise pool limits beyond the database maximum.

## Rollback

1. Stop new deployments.
2. Roll back the application image to the previous immutable tag.
3. Database migrations must be backward compatible for at least one release.
4. Use Alembic downgrade only after a tested backup and explicit incident-lead approval.

## Backup and restore

- Run `scripts/backup_restore.sh backup` with
  `BACKUP_ENCRYPTION_PASSWORD` supplied by the secret manager.
- Verify every backup with `scripts/backup_restore.sh verify <file>`.
- Perform a restore drill at least monthly in an isolated environment.
- Target RPO: 24 hours. Target RTO: 4 hours.

## Security incident

- Revoke affected API keys and refresh tokens.
- Rotate application, database, SMTP, monitoring, Telegram, and provider secrets.
- Preserve audit events and infrastructure logs.
- Follow applicable GDPR, KVKK, CCPA, and contractual notification timelines.
