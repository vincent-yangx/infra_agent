from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from agents.state import AgentState
from tools.file_readers import read_text_file


ErrorType = Literal[
    "database_query_timeout",
    "gateway_504",
    "connection_pool_pressure",
    "high_latency",
    "lock_contention",
    "memory_pressure",
    "unknown",
]

MetricName = Literal[
    "cpu_usage_percent",
    "memory_usage_percent",
    "active_connections",
    "max_connections",
    "active_locks",
    "slow_queries",
    "avg_query_latency_ms",
    "disk_usage_percent",
]


class LogExtraction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    relevant_log_lines: list[str] = Field(
        description="Exact log lines from the input that are relevant to the user's query."
    )

    log_findings: list[str] = Field(
        description="Concise English findings extracted from the relevant logs."
    )

    detected_services: list[str] = Field(
        description="Microservices involved in the relevant abnormal logs."
    )

    detected_errors: list[ErrorType] = Field(
        description="Canonical error types inferred from the logs."
    )

    requires_metrics: bool = Field(
        description="Whether metrics are needed to verify infrastructure, database, latency, or resource-related causes."
    )

    metrics_to_check: list[MetricName] = Field(
        description=(
            "Canonical metric names that should be checked next. "
            "Only select from: cpu_usage_percent, memory_usage_percent, "
            "active_connections, max_connections, active_locks, "
            "slow_queries, avg_query_latency_ms, disk_usage_percent."
        )
    )


llm = ChatOpenAI(
    temperature=0,
    model="gpt-4o-mini",
)

structured_llm = llm.with_structured_output(LogExtraction)


def log_agent(state: AgentState):
    """
    Use an LLM to extract query-relevant log evidence in a structured format.
    """

    query = state["user_query"]

    try:
        raw_logs = read_text_file("app_logs.txt")
    except FileNotFoundError:
        return {
            "raw_logs": None,
            "log_findings": ["No application log file was found."],
            "evidence": ["Application logs were unavailable."],
            "next_action": "retrieve_docs",
        }

    prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are a senior SRE engineer.

Your task is to analyze system logs and extract only the information relevant to the user's troubleshooting request.

Rules:
- Do not invent facts that are not present in the logs.
- Use English for all findings and labels.
- Return exact relevant log lines when possible.
- Distinguish symptoms from possible root causes.
- If the logs suggest database, network, latency, CPU, memory, lock, or connection-pool issues, set requires_metrics to true.
- Use only the canonical error labels allowed by the schema.
- Use only the canonical metric names allowed by the schema.

Available metric names:
- cpu_usage_percent: database CPU usage percentage
- memory_usage_percent: database memory usage percentage
- active_connections: current active database connections
- max_connections: maximum allowed database connections
- active_locks: number of active database locks
- slow_queries: number of slow database queries
- avg_query_latency_ms: average database query latency in milliseconds
- disk_usage_percent: database disk usage percentage

Metric selection rules:
- If logs show database query timeout, include avg_query_latency_ms, slow_queries, active_locks, active_connections, and cpu_usage_percent.
- If logs show connection pool pressure, include active_connections and max_connections.
- If logs show lock contention or lock wait, include active_locks and slow_queries.
- If logs show high latency, include avg_query_latency_ms.
- If logs show memory pressure or OOM, include memory_usage_percent.
- Do not invent metric names.
"""
    ),
    (
        "user",
        """
User troubleshooting request:
{query}

System logs:
{logs}
"""
    )
])

    chain = prompt | structured_llm
    result: LogExtraction = chain.invoke({
        "query": query,
        "logs": raw_logs,
    })

    metric_related_errors = {
        "database_query_timeout",
        "connection_pool_pressure",
        "high_latency",
        "lock_contention",
        "memory_pressure",
    }

    should_check_metrics = (
        result.requires_metrics
        or any(error in metric_related_errors for error in result.detected_errors)
    )

    next_action = "check_metrics" if should_check_metrics else "retrieve_docs"

    evidence = []
    evidence.extend(result.log_findings)
    evidence.extend([f"Relevant log line: {line}" for line in result.relevant_log_lines])

    return {
        "raw_logs": raw_logs,
        "relevant_logs": result.relevant_log_lines,
        "log_findings": result.log_findings,
        "detected_services": result.detected_services,
        "detected_errors": result.detected_errors,
        "evidence": evidence,
        "metrics_to_check": result.metrics_to_check,
        "next_action": next_action,
    }