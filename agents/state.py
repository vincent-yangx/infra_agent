from typing import TypedDict, List, Dict, Any, Optional, Literal, Annotated
from operator import add

NextAction = Literal[
    "analyze_logs",
    "check_metrics",
    "retrieve_docs",
    "diagnose",
    "end"
]

class AgentState(TypedDict):
    user_query: str

    raw_logs: Optional[str]
    relevant_logs: Annotated[List[str], add]

    raw_metrics: Optional[Dict[str, Any]]

    log_findings: Annotated[List[str], add]
    detected_services: Annotated[List[str], add]
    detected_errors: Annotated[List[str], add]

    metric_findings: Annotated[List[str], add]
    metrics_to_check: Annotated[List[str], add]

    retrieved_docs: Annotated[List[str], add]
    evidence: Annotated[List[str], add]
    hypothesis: Annotated[List[str], add]

    retrieval_query: Optional[str]

    next_action: NextAction

    final_report: Optional[str]

def create_initial_state(user_query: str) -> AgentState:
    return {
        "user_query": user_query,
        "raw_logs": None,
        "relevant_logs": [],

        "raw_metrics": {},

        "log_findings": [],
        "detected_services": [],
        "detected_errors": [],

        "metric_findings": [],
        "metrics_to_check": [],

        "retrieval_docs": [],
        "evidence": [],
        "hypothesis": [],

        "retrieval_query": None,
        "next_action": "analyze_logs",
        "final_report": None
    }