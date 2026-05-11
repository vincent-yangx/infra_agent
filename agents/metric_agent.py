from agents.state import AgentState
from tools.file_readers import read_json_file

def normalize_metric_name(name: str) -> str:
    return name.lower().strip().replace(" ", "_").replace("-", "_")


def should_check(metric_name: str, metrics_to_check: list[str]) -> bool:
    if not metrics_to_check:
        return True

    normalized_targets = {
        normalize_metric_name(m) for m in metrics_to_check
    }

    alias_map = {
        "cpu_usage_percent": {
            "cpu_usage_percent", "cpu", "db_cpu", "db_cpu_usage",
            "cpu_usage", "database_cpu_usage"
        },
        "memory_usage_percent": {
            "memory_usage_percent", "memory", "db_memory",
            "memory_usage", "database_memory_usage"
        },
        "active_connections": {
            "active_connections", "db_connections",
            "connection_count", "connections"
        },
        "max_connections": {
            "max_connections", "connection_limit", "max_db_connections"
        },
        "active_locks": {
            "active_locks", "db_locks", "lock_count", "locks"
        },
        "slow_queries": {
            "slow_queries", "slow_query_count", "slow_sql"
        },
        "avg_query_latency_ms": {
            "avg_query_latency_ms", "avg_query_latency",
            "query_latency", "db_latency", "average_query_latency"
        },
        "disk_usage_percent": {
            "disk_usage_percent", "disk", "disk_usage", "db_disk_usage"
        },
    }

    aliases = alias_map.get(metric_name, {metric_name})
    normalized_aliases = {
        normalize_metric_name(alias) for alias in aliases
    }

    return bool(normalized_targets.intersection(normalized_aliases))


def metric_agent (state: AgentState):
    try:
        raw_metrics = read_json_file("db_metrics.json")
    except FileNotFoundError:
        return {
            "raw_metrics": None,
            "metric_findings": ["No database metrics file was found"],
            "evidence": [
                "Database metrics were unavailable, so the diagonsis relies on logs and knowledge base retrieval."
            ],
            "next_action": "retrieve_docs"
        }

    metrics_to_check = state.get("metrics_to_check", [])
    metric_findings = []
    evidence = []
    hypothesis = []
    
    metrics = raw_metrics.get("metrics", {})
    events = raw_metrics.get("events", [])

    cpu_usage = metrics.get("cpu_usage_percent")
    memory_usage = metrics.get("memory_usage_percent")
    active_connections = metrics.get("active_connections")
    max_connections = metrics.get("max_connections")
    active_locks = metrics.get("active_locks")
    slow_queries = metrics.get("slow_queries")
    avg_query_latency_ms = metrics.get("avg_query_latency_ms")
    disk_usage = metrics.get("disk_usage_percent")

    # 1. CPU usage
    if should_check("cpu_usage_percent", metrics_to_check):
        if cpu_usage is not None and cpu_usage >= 90:
            finding = f"Database CPU usage was very high: {cpu_usage}%."
            metric_findings.append(finding)
            evidence.append(finding)
            hypothesis.append(
                "Database overload may have contributed to slow queries or timeouts."
            )

    # 2. Memory usage
    if should_check("memory_usage_percent", metrics_to_check):
        if memory_usage is not None and memory_usage >= 90:
            finding = f"Database memory usage was high: {memory_usage}%."
            metric_findings.append(finding)
            evidence.append(finding)
            hypothesis.append(
                "Memory pressure may have affected database performance."
            )

    # 3. Active connections
    if (
    should_check("active_connections", metrics_to_check)
    or should_check("max_connections", metrics_to_check)
    ):
        if active_connections is not None and max_connections is not None:
            finding = (
                f"Database active connections reached {active_connections} "
                f"out of {max_connections}."
            )
            metric_findings.append(finding)
            evidence.append(finding)

            if max_connections > 0:
                connection_ratio = active_connections / max_connections

                if connection_ratio >= 0.9:
                    hypothesis.append(
                        "Database connection pressure may have caused requests to wait or timeout."
                    )

    # 4. Active locks
    if should_check("active_locks", metrics_to_check):
        if active_locks is not None and active_locks > 0:
            finding = f"Database active locks were detected: {active_locks}."
            metric_findings.append(finding)
            evidence.append(finding)
            hypothesis.append(
                "Database lock contention may have delayed query execution."
            )

    # 5. Slow queries
    if should_check("slow_queries", metrics_to_check):
        if slow_queries is not None and slow_queries > 0:
            finding = f"Database slow queries were observed: {slow_queries}."
            metric_findings.append(finding)
            evidence.append(finding)
            hypothesis.append(
                "Slow queries may have increased application request latency."
            )

    # 6. Average query latency
    if should_check("avg_query_latency_ms", metrics_to_check):
        if avg_query_latency_ms is not None and avg_query_latency_ms >= 5000:
            finding = f"Average database query latency was high: {avg_query_latency_ms} ms."
            metric_findings.append(finding)
            evidence.append(finding)
            hypothesis.append(
                "High database query latency likely contributed to application timeouts."
            )

    # 7. Disk usage
    if should_check("disk_usage_percent", metrics_to_check):
        if disk_usage is not None and disk_usage >= 90:
            finding = f"Database disk usage was high: {disk_usage}%."
            metric_findings.append(finding)
            evidence.append(finding)
            hypothesis.append(
                "High disk usage may have affected database write or query performance."
            )

    # 8. Events
    for event in events:
        event_name = event.get("event", "")
        event_time = event.get("time", "")

        if event_name == "monthly_finance_batch_started":
            finding = f"Monthly finance batch job started at {event_time}."
            metric_findings.append(finding)
            evidence.append(finding)
            hypothesis.append(
                "The monthly finance batch job may have caused database lock contention or high CPU usage."
            )

        elif event_name == "lock_wait_timeout_detected":
            finding = f"Database lock wait timeout was detected at {event_time}."
            metric_findings.append(finding)
            evidence.append(finding)
            hypothesis.append(
                "Lock wait timeout suggests that queries were blocked by database locks."
            )

        elif event_name == "connection_pool_near_limit":
            finding = f"Database connection pool was near limit at {event_time}."
            metric_findings.append(finding)
            evidence.append(finding)
            hypothesis.append(
                "Connection pool saturation may have amplified request timeouts."
            )

    if not metric_findings:
        metric_findings.append("No abnormal database metrics were detected for the requested checks.")
        evidence.append("Database metrics did not show obvious abnormal signals for the requested checks.")

    return {
        "raw_metrics": raw_metrics,
        "metric_findings": metric_findings,
        "evidence": evidence,
        "hypothesis": hypothesis,
        "next_action": "retrieve_docs",
    }

