# 1. Architecture Decisions

Date: 2026-06-19

## Status

Accepted

## Context

ResumeMatch AI requires a system capable of handling long-running AI inference tasks (analyzing CVs and JDs, generating outreach drafts) while providing real-time feedback to users over WebSockets. The system must also be easily self-hostable.

## Decisions

We have chosen the following stack:

1. **FastAPI (Python)**: Provides high-performance async capabilities, native WebSocket support, and excellent integration with the Python AI/ML ecosystem.
2. **Next.js (React)**: Enables a rich, dynamic frontend with App Router, supporting both server-side rendering for SEO and interactive client-side components for real-time progress tracking.
3. **Celery with Redis**: Used for asynchronous task queuing. AI generation (especially with local Ollama) can take 30+ seconds. Processing this in the main API thread would block the event loop and lead to timeouts. Celery idempotently processes tasks and uses Redis Pub/Sub to send progress updates back to the FastAPI WebSocket handlers.
4. **PostgreSQL**: Serves as the primary relational database for users, analysis history, and eventual feedback loops. Chosen for reliability and JSONB support for unstructured AI results.
5. **Docker Compose**: Standardizes the self-hosting deployment, orchestrating the API, Frontend, Worker, Redis, and PostgreSQL containers in a single network.

## Consequences

- **Pros**: Clear separation of concerns (API vs. Worker), scalable, real-time UX without HTTP timeouts, robust and self-contained deployment.
- **Cons**: Increased operational complexity (requires Redis and Celery worker instead of a single monolithic process). However, Docker Compose mitigates this complexity for end-users.
