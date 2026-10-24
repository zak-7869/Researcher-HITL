from prometheus_client import Counter, Histogram
REQUESTS = Counter("research_api_requests_total", "API requests", ["route", "status"])
RUNS = Counter("research_runs_total", "Research runs", ["status"])
RUN_DURATION = Histogram("research_run_duration_seconds", "Research run duration")
NODE_ERRORS = Counter("research_graph_node_errors_total", "Graph node errors", ["node"])
