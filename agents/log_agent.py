from agents.state import AgentState
from tools.file_readers import read_text_file

def log_agent(state: AgentState):
    """
    Extract important error signals from application logs
    """
    try:
        raw_logs = read_text_file("app_logs.txt")
    except FileNotFoundError:
        return {
            "raw_logs": None,
            "log_findings": ["No application log file was found."],
            "evidence": ["Application logs were unavailable."],
            "next_action": "retrieve_docs",
        }

    log_findings = []
    detected_services = []
    detected_errors = []
    evidence = []

    lower_logs = raw_logs.lower()
    """
    Future problems:
      keywords matching problems
      Synonyms in keywords
      incresing keywords
    """
    if "order-service" in lower_logs:
        detected_services.append("order-service")

    if "payment-service" in lower_logs:
        detected_services.append("payment-service")

    if "api-gateway" in lower_logs:
        detected_services.append("api-gateway")

    if "database query timeout" in lower_logs or "db connection timeout" in lower_logs:
        detected_errors.append("database_query_timeout")
        finding = "Application logs show database query timeout."
        log_findings.append(finding)
        evidence.append(finding)
    
    if "504 gateway timeout" in lower_logs:
        detected_errors.append("504_gateway_timeout")
        finding = "API gateway returned 504 gateway timeout."
        log_findings.append(finding)
        evidence.append(finding)

    if "connection pool near limit" in lower_logs or "too many active database connections" in lower_logs:
        detected_errors.append("connection_pool_near_limit")
        finding = "Application logs suggest database connection pool pressure."
        log_findings.append(finding)
        evidence.append(finding)

    if "latency p95 increased" in lower_logs:
        detected_errors.append("high_latency")
        finding = "Checkout latency p95 increased significantly."
        log_findings.append(finding)
        evidence.append(finding)

    if any("database" in error or "connection" in error for error in detected_errors):
        next_action = "check_metrics"
    else:
        next_action = "retrieve_docs"

    return {
        "raw_logs": raw_logs,
        "log_findings": log_findings,
        "detected_services": detected_services,
        "detected_errors": detected_errors,
        "evidence": evidence,
        "next_action": next_action
    }

    

    
