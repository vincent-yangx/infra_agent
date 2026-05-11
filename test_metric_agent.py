"""
 normal situation
"""
# from agents.state import create_initial_state
# from agents.metric_agent import metric_agent

# state = create_initial_state("Investigate why checkout failed around 2 AM.")

# state["metrics_to_check"] = [
#     "cpu_usage_percent",
#     "active_connections",
#     "max_connections",
#     "active_locks",
#     "slow_queries",
#     "avg_query_latency_ms",
# ]

# result = metric_agent(state)

# print("metric_findings:")
# for item in result["metric_findings"]:
#     print("-", item)

# print("\nhypothesis:")
# for item in result["hypothesis"]:
#     print("-", item)

# print("\nnext_action:", result["next_action"])

'''
check when metrics to check is null
'''
# from agents.state import create_initial_state
# from agents.metric_agent import metric_agent

# state = create_initial_state("Investigate checkout timeout.")
# state["metrics_to_check"] = []

# result = metric_agent(state)

# print(result["metric_findings"])
# print(result["next_action"])

"""
check if should_check() works
"""

from agents.state import create_initial_state
from agents.metric_agent import metric_agent

state = create_initial_state("Investigate possible lock contention.")
state["metrics_to_check"] = [
    "active_locks",
    "slow_queries",
]
result = metric_agent(state)

print(result["metric_findings"])