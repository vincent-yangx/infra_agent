from langgraph.graph import StateGraph, START, END

from agents.state import AgentState
from agents.log_agent import log_agent
from agents.metric_agent import metric_agent
from agents.rag_agent import rag_agent
from agents.diagnosis_agent import diagnosis_agent

def route_after_log(state: AgentState) -> str:
    """
    Decide where to go after Log Agent.

    If Log Agent determines that metrics are needed,
    go to Metric Agent. Otherwise, go directly to RAG agent.
    """

    next_action = state.get("next-action", "retrieve_docs")

    if next_action == "check_metrics":
        return "metric_agent"

    if next_action == "retrieve_docs":
        return "rag_agent"
    
    return "rag_agent"

def route_after_metric(state: AgentState) -> str:
    """
    Decide where to go after Metric Agent.

    In this MVP, Metric Agent should usually send the workflow 
    to RAG Agent after analyzing metrics.
    """
    next_action = state.get("next-action", "retrieve_docs")

    if next_action == "retrieve_docs":
        return "rag_agent"

    if next_action == "diagnose":
        return "diagnosis_agent"
    
    return "rag_agent"

def route_after_rag(state: AgentState) -> str:
    """
    Decide where to go after RAG agent
    """
    next_action = state.get("next-action", "diagnose")

    if next_action == "diagnose":
        return "diagnosis_agent"
    
    return "diagnosis_agent"

def build_graph():
    """
    Build and compile the LangGraph workflow.
    """

    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("log_agent", log_agent)
    graph_builder.add_node("metric_agent", metric_agent)
    graph_builder.add_node("rag_agent", rag_agent)
    graph_builder.add_node("diagnosis_agent", diagnosis_agent)

    graph_builder.add_edge(START, "log_agent")

    graph_builder.add_conditional_edges(
        "log_agent",
        route_after_log,
        {
            "metric_agent": "metric_agent",
            "rag_agent": "rag_agent"
        }
    )

    graph_builder.add_conditional_edges(
        "metric_agent",
        route_after_metric,
        {
            "rag_agent": "rag_agent",
            "diagnosis_agent": "diagnosis_agent"
        }
    )

    graph_builder.add_conditional_edges(
        "rag_agent",
        route_after_rag,
        {
            "diagnosis_agent": "diagnosis_agent",
        }
    )

    graph_builder.add_edge("diagnosis_agent", END)

    return graph_builder.compile()
    

