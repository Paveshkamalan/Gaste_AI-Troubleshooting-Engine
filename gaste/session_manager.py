import time
import uuid
from typing import Dict
from config import settings

# In-memory store
sessions: Dict[str, dict] = {}

def create_session(query: str, current_tier: int = 1) -> str:
    session_id = f"sess_{uuid.uuid4().hex[:8]}"
    sessions[session_id] = {
        "session_id": session_id,
        "issue": query,
        "current_tier": current_tier,
        "failed_steps": [],
        "completed_steps": [],
        "created_at": time.time(),
        "expires_at": time.time() + settings.SESSION_TTL_SECONDS
    }
    return session_id

def get_session(session_id: str) -> dict:
    session = sessions.get(session_id)
    if session and time.time() < session["expires_at"]:
        # refresh TTL
        session["expires_at"] = time.time() + settings.SESSION_TTL_SECONDS
        return session
    
    # Clean up if expired
    if session:
        del sessions[session_id]
    return None

def update_session(session_id: str, updates: dict):
    session = get_session(session_id)
    if session:
        session.update(updates)
        session["expires_at"] = time.time() + settings.SESSION_TTL_SECONDS

def record_failure(session_id: str, failed_step: str):
    session = get_session(session_id)
    if session:
        if failed_step not in session["failed_steps"]:
            session["failed_steps"].append(failed_step)
        session["current_tier"] += 1
        return session
    return None

def cleanup_expired():
    now = time.time()
    expired = [sid for sid, sess in sessions.items() if now > sess["expires_at"]]
    for sid in expired:
        del sessions[sid]
