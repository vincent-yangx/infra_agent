from agents.state import AgentState
from tools.faiss_retriever import retrieve_docs

def build_retrieval_query(state: AgentState) -> str:
    query_parts = []

    query_parts.extend(state.get("hypothesis", []))
    query_parts.extend(state.get("detected_errors", []))
    query_parts.extend(state.get("log_findings", []))
    query_parts.extend(state.get("metric_findings", []))
    query_parts.extend(state.get("metrics_to_check", []))

    query_parts = [
        str(item).strip()
        for item in query_parts
        if item is not None and str(item).strip()
    ]

    if query_parts:
        return " ".join(query_parts)
    
    # Fallback: if no structured findings exists in AgentState, use user query
    return state.get("user_query", "")

def rag_agent(state: AgentState):
    """
    Retrieve relevant runbook / knowledge base documents using FAISS
    """

    retrieval_query = build_retrieval_query(state)

    if not retrieval_query.strip():
        return {
            "retrieval_query": retrieval_query,
            "retrieved_docs": [],
            "evidence": ["No retrieval query could be constructed"],
            "next_action": "diagnose"
        }

    try:
        docs = retrieve_docs(
            query= retrieval_query,
            top_k = 3,
            kb_file_name= "kb_docs.txt"
        )
    except FileNotFoundError:
        return {
            "retrieval_query": retrieval_query,
            "retrieved_docs": [],
            "evidence": ["Knowledge base file was not found."],
            "next_action": "diagnose"
        }
    
    except ValueError as e:
        return {
            "retrieval_query": retrieval_query,
            "retrieved_docs": [],
            "evidence": [f"RAG retrieval failed: {str(e)}"],
            "next_action": "diagnose"
        }
    
    evidence = [
        "Relevant troubleshooting documents were retrieved from the knowledge base."
    ]

    return {
        "retrieval_query": retrieval_query,
        "retrieved_docs": docs,
        "evidence": evidence,
        "next_action": "diagnose"
    }