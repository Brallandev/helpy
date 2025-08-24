from typing import Dict, Any

AGENT_SESSIONS: Dict[str, Dict[str, Any]] = {}

def create_session(session_id: str, meta_agent: Any):
    """
    Store a new session for a patient
    """
    AGENT_SESSIONS[session_id] = {
        "meta_agent": meta_agent,
        "questions_agent": meta_agent.questions_agent,
        "critical_agents": meta_agent.critical_agents
    }

def get_session(session_id: str) -> Dict[str, Any]:
    """
    Retrieve the agents/session data for a patient
    """
    return AGENT_SESSIONS.get(session_id)

def remove_session(session_id: str):
    """
    Remove session after completion
    """
    if session_id in AGENT_SESSIONS:
        del AGENT_SESSIONS[session_id]

def get_num_sessions() -> int:
    """
    Get the number of active sessions
    """
    return len(AGENT_SESSIONS)
