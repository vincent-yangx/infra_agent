from dotenv import load_dotenv
load_dotenv(override=True)

from agents.state import create_initial_state
from agents.rag_agent import rag_agent

state = create_initial_state("Investigate why checkout failed around 2 AM.")

state["detected_errors"] = [
    "database_query_timeout",
    "gateway_504",
    "connection_pool_pressure",
]

state["log_findings"] = [
    "The order-service experienced a database query timeout.",
    "The API gateway returned 504 Gateway Timeout.",
]

state["metric_findings"] = [
    "Database CPU usage was very high: 99%.",
    "Database active locks were detected: 12.",
    "Database slow queries were observed: 37.",
    "Monthly finance batch job started at 2026-05-01 01:59:45.",
]

state["hypothesis"] = [
    "The monthly finance batch job may have caused database lock contention or high CPU usage.",
]

state["metrics_to_check"] = [
    "cpu_usage_percent",
    "active_locks",
    "slow_queries",
    "avg_query_latency_ms",
]

result = rag_agent(state)

print("Retrieval Query:")
print(result["retrieval_query"])

print("\nRetrieved Docs:")
for doc in result["retrieved_docs"]:
    print("\n---")
    print(doc)

print("\nNext Action:")
print(result["next_action"])