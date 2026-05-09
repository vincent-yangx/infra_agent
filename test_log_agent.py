from dotenv import load_dotenv
load_dotenv(override=True)

from agents.state import create_initial_state

from agents.log_agent import log_agent

def main():
    state = create_initial_state(
        "Investigate why the order checkout system failed around 2 AM."
    )

    result = log_agent(state)

    print("\n===== RAW LOGS LOADED =====")
    print(result.get("raw_logs") is not None)

    print("\n===== RELEVANT LOGS =====")
    for line in result.get("relevant_logs", []):
        print("-", line)

    print("\n===== LOG FINDINGS =====")
    for finding in result.get("log_findings", []):
        print("-", finding)

    print("\n===== DETECTED SERVICES =====")
    print(result.get("detected_services", []))

    print("\n===== DETECTED ERRORS =====")
    print(result.get("detected_errors", []))

    print("\n===== EVIDENCE =====")
    for e in result.get("evidence", []):
        print("-", e)

    print("\n===== NEXT ACTION =====")
    print(result.get("next_action"))


if __name__ == "__main__":
    main()