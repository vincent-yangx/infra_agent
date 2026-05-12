from dotenv import load_dotenv
load_dotenv(override=True)

from graph import build_graph
from agents.state import create_initial_state

def main():
    graph = build_graph()

    user_query = "Investigate why checkout failed around 2 AM."

    initial_state = create_initial_state(user_query)

    result = graph.invoke(initial_state)

    print("\n===== FINAL DIAGNOSIS REPORT =====\n")
    print(result.get("final_report", "No final report generated."))


if __name__ == "__main__":
    main()