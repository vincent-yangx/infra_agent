from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from agents.state import AgentState

ConfidenceLevel = Literal["High","Medium","Low"]

class RootCauseCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank : int = Field(
        description= "Ranking of the root-cause candidate, where 1 is the most likely."
    )

    root_cause: str = Field(
        description="A concise root-cause hypothesis."
    )

    confidence: ConfidenceLevel = Field(
        description="Confidence level for this root-cause candidate."
    )

    evidence: list[str] = Field(
        description="Specific evidence supporting this root-cause candidate."
    )

    recommended_actions: list[str] = Field(
        description="Concrete remediation or investigation actions."
    )

class DiagnosisResult(BaseModel):
    model_config = ConfigDict(extra = "forbid")

    summary: str = Field(
        description="A concise summary of what likely happened."
    )

    root_causes: list[RootCauseCandidate] = Field(
        description="Ranked root-cause candidates."
    )

    missing_evidence: list[str] = Field(
        description="Important evidence that is missing or still needs to be checked."
    )

    final_report: str = Field(
        description="A user-facing final diagnosis report in clear English."
    )

llm = ChatOpenAI(
    temperature= 0,
    model= "gpt-4o-mini"
)

structured_llm = llm.with_structured_output(DiagnosisResult)

def _format_list(items: list[str]) -> str:
    """
    format a list of strings for prompt input
    """

    if not items:
        return "None"

    return "\n".join(f"- {item}" for item in items)

def diagnosis_agent(state: AgentState):
    user_query = state.get("user_query", [])

    log_findings = state.get("log_findings", [])
    metric_findings = state.get("metric_findings", [])
    retrieved_docs = state.get("retrieved_docs", [])
    hypothesis = state.get("hypothesis", [])
    evidence = state.get("evidence", [])

    detected_services = state.get("detected_services", [])
    detected_errors = state.get("detected_errors", [])
    relevant_logs = state.get("relevant_logs", [])

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a senior SRE engineer performing incident diagnosis and root cause analysis.

Your task:
- Use the provided logs, metrics, retrieved runbooks, and hypotheses.
- Generate a clear final diagnosis report.
- Rank the most likely root causes.
- Support every root cause with concrete evidence.
- Do not invent facts that are not present in the provided evidence.
- Distinguish symptoms from root causes.
- If evidence is missing, state what still needs to be checked.
- Use English.
"""
            ),
            (
                "user",
                """
User troubleshooting request:
{user_query}

Detected services:
{detected_services}

Detected errors:
{detected_errors}

Relevant log lines:
{relevant_logs}

Log findings:
{log_findings}

Metric findings:
{metric_findings}

Candidate hypotheses from previous agents:
{hypothesis}

Retrieved knowledge base / runbook documents:
{retrieved_docs}

All collected evidence:
{evidence}

Please produce:
1. A concise incident summary.
2. Ranked root-cause candidates.
3. Evidence for each root cause.
4. Recommended actions.
5. Missing evidence or follow-up checks.
6. A final user-facing diagnosis report.
"""
            ),
        ]
    )

    chain = prompt| structured_llm
    
    result: DiagnosisResult = chain.invoke(
    {
        "user_query": user_query,
        "detected_services": _format_list(detected_services),
        "detected_errors": _format_list(detected_errors),
        "relevant_logs": _format_list(relevant_logs),
        "log_findings": _format_list(log_findings),
        "metric_findings": _format_list(metric_findings),
        "hypothesis": _format_list(hypothesis),
        "retrieved_docs": _format_list(retrieved_docs),
        "evidence": _format_list(evidence),
    }
    )

    return {
        "final_report": result.final_report,
        "hypothesis": [
            candidate.root_cause for candidate in result.root_causes
        ],
        "evidence": [
            item for candidate in result.root_causes
            for item in candidate.evidence
        ],
        "next_action": "end"
    }
