from prometheus_client import Counter, Gauge, Histogram

db_pool_size = Gauge("db_pool_size", "Configured database connection pool size")
db_pool_active = Gauge(
    "db_pool_active_connections",
    "Active database connections observed by PostgreSQL",
)
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)
analysis_tasks_total = Counter(
    "analysis_tasks_total",
    "Analysis task outcomes",
    ["status"],
)
llm_provider_requests_total = Counter(
    "llm_provider_requests_total",
    "LLM provider request outcomes",
    ["provider", "status"],
)
celery_queue_depth = Gauge(
    "celery_queue_depth",
    "Current Redis queue depth",
    ["queue"],
)
