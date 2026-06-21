# Service level objectives

These objectives apply to the hosted production service. Self-hosted operators
should adapt them to their own infrastructure.

| Signal | Objective | Window |
|---|---:|---:|
| API availability, excluding planned maintenance | 99.9% | 30 days |
| Authenticated API p95 latency, excluding AI jobs | < 500 ms | 30 days |
| Analysis queue acceptance success | 99.5% | 30 days |
| Analysis completion, when a provider is healthy | 98% | 30 days |
| WebSocket or polling delivery of a final result | 99.5% | 30 days |

The monthly availability error budget is 43 minutes. Feature releases stop
when more than 50% of the budget is consumed before the middle of the window,
or when the entire budget is consumed at any time.

Alerts must be based on user-visible symptoms. Dashboard panels should include
request rate, error rate, latency, worker availability, queue depth, provider
errors, database saturation, and analysis completion rate.
