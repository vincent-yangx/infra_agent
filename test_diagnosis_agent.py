from dotenv import load_dotenv
load_dotenv(override=True)

from agents.state import create_initial_state
from agents.diagnosis_agent import diagnosis_agent

state = create_initial_state("Investigate why checkout failed around 2 AM.")

state["detected_services"] = [
    "order-service",
    "payment-service",
    "api-gateway",
]

state["detected_errors"] = [
    "database_query_timeout",
    "gateway_504",
    "connection_pool_pressure",
]

state["relevant_logs"] = [
    "[2026-05-01 02:00:08] ERROR order-service: Database query timeout after 30000ms while waiting for query result",
    "[2026-05-01 02:01:35] WARN api-gateway: Upstream order-service returned 504 Gateway Timeout",
]

state["log_findings"] = [
    "The order-service experienced a database query timeout.",
    "The API gateway returned 504 Gateway Timeout.",
]

state["metric_findings"] = [
    "Database CPU usage was very high: 99%.",
    "Database active connections reached 480 out of 500.",
    "Database active locks were detected: 12.",
    "Database slow queries were observed: 37.",
    "Average database query latency was high: 8200 ms.",
    "Monthly finance batch job started at 2026-05-01 01:59:45.",
]

state["hypothesis"] = [
    "The monthly finance batch job may have caused database lock contention or high CPU usage.",
    "Database lock contention may have delayed query execution.",
    "Connection pool saturation may have amplified request timeouts.",
]

state["retrieved_docs"] = [
    """
# Runbook: Monthly Finance Batch Job Lock Contention

Symptoms:
- Checkout or order APIs fail around the beginning of the month.
- Database CPU usage becomes very high.
- Active locks increase.
- Slow queries increase.
- Application logs show database timeout or 504 Gateway Timeout.

Recommended Actions:
- Move the finance batch job to an off-peak time window.
- Reduce the lock scope of the batch job.
- Split the batch job into smaller chunks.
"""
]

state["evidence"] = (
    state["log_findings"]
    + state["metric_findings"]
    + state["retrieved_docs"]
)

result = diagnosis_agent(state)

print(result["final_report"])
print(result["next_action"])