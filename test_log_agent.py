from agents.state import create_initial_state
from agents.log_agent import log_agent

state = create_initial_state("Investigate why the order system went down around 2 AM last night.")
result = log_agent(state)

print(result)