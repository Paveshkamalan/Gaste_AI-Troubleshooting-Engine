import time
from fastapi import FastAPI, Header, HTTPException
from typing import Optional
import database
import engine
import session_manager
from schema import (
    TroubleshootRequest, ContextDeeplinkResponse,
    InteractiveRequest, InteractiveResponse, ActionablePlan
)

app = FastAPI(title="GASTE API")

startup_complete = False

@app.on_event("startup")
async def startup_event():
    global startup_complete
    print("Initializing database...")
    database.setup_database()
    print("Initializing engine...")
    engine.init_engine()
    startup_complete = True
    print("GASTE API started successfully.")

@app.get("/health")
def health_check():
    if not startup_complete:
        raise HTTPException(status_code=503, detail="System initializing")
    return {"status": "ok"}

@app.post("/v1/troubleshoot", response_model=ContextDeeplinkResponse)
def troubleshoot(request: TroubleshootRequest, x_session_id: Optional[str] = Header(None)):
    start_time = time.time()
    
    # Process
    response = engine.process_troubleshoot_request(request.query, request.siis_response)
    
    # Session handling
    if not x_session_id:
        session_id = session_manager.create_session(request.query)
        # We can inject session ID in headers or payload in a real app, 
        # but the schema ContextDeeplinkResponse doesn't have a session field.
        # We'll just maintain it on backend for when they hit interactive endpoint.
        
    latency_ms = int((time.time() - start_time) * 1000)
    print(f"Request latency: {latency_ms}ms")
    
    return response

@app.post("/v1/troubleshoot/interactive", response_model=InteractiveResponse)
def interactive_troubleshoot(request: InteractiveRequest, x_session_id: str = Header(...)):
    start_time = time.time()
    
    session = session_manager.get_session(x_session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
        
    # Mark the current step as failed based on the query or implicit logic
    session_manager.record_failure(x_session_id, request.query)
    updated_session = session_manager.get_session(x_session_id)
    
    tier = updated_session["current_tier"]
    
    plan = [
        ActionablePlan(
            step=tier,
            action=f"Fallback action for tier {tier}",
            reason="Previous step did not resolve the issue"
        )
    ]
    
    response = InteractiveResponse(
        session_id=x_session_id,
        current_tier=tier,
        status="in_progress",
        message="Let's try the next troubleshooting step.",
        actionable_plan=plan,
        retrieval_used=False
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    print(f"Interactive Request latency: {latency_ms}ms")
    
    return response
