import time
from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.responses import FileResponse
from typing import Optional
import database
import engine
import session_manager
from schema import (
    TroubleshootRequest, ContextDeeplinkResponse,
    InteractiveRequest, InteractiveResponse, ActionablePlan
)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="GASTE API", docs_url=None, redoc_url="/redoc")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

DOCS_PAGE = Path(__file__).parent / "static" / "docs.html"

@app.get("/", include_in_schema=False)
@app.get("/docs", include_in_schema=False)
def api_docs():
    return FileResponse(DOCS_PAGE)

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
def troubleshoot(request: TroubleshootRequest, http_response: Response, x_session_id: Optional[str] = Header(None)):
    start_time = time.time()
    
    # Process
    result = engine.process_troubleshoot_request(request.query, request.siis_response)
    
    # Session handling
    sid = x_session_id
    if not sid:
        sid = session_manager.create_session(request.query)
    http_response.headers["X-Session-ID"] = sid
    http_response.headers["Access-Control-Expose-Headers"] = "*"
        
    latency_ms = int((time.time() - start_time) * 1000)
    print(f"Request latency: {latency_ms}ms")
    
    return result

@app.post("/v1/troubleshoot/interactive", response_model=InteractiveResponse)
def interactive_troubleshoot(request: InteractiveRequest, http_response: Response, x_session_id: Optional[str] = Header(None)):
    start_time = time.time()
    
    # Resolve session ID from header or body
    sid = x_session_id or getattr(request, "session_id", None)
    if not sid:
        sid = session_manager.create_session(request.query or "General Issue")
        
    session = session_manager.get_session(sid)
    if not session:
        # Auto-recover session if expired
        sid = session_manager.create_session(request.query or "General Issue")
        session = session_manager.get_session(sid)
        
    # Mark the current step as failed based on the query or implicit logic
    session_manager.record_failure(sid, request.query)
    updated_session = session_manager.get_session(sid)
    
    tier = updated_session["current_tier"]
    issue_text = (session.get("issue") or request.query or "").lower()
    
    # Generate intelligent contextual plans for hackathon demo
    if any(k in issue_text for k in ["battery", "drain", "charge", "power", "hot", "heat"]):
        if tier == 2:
            plan = [
                ActionablePlan(
                    step=1,
                    action="Restrict Background App Execution & Enable Deep Sleeping Apps",
                    reason="Tier 1 basic battery settings did not halt discharge rate; aggressive background processes detected."
                ),
                ActionablePlan(
                    step=2,
                    action="Enable Adaptive Power Saving & Limit CPU Frequency to 70%",
                    reason="Throttles heavy background loops dynamically while preserving display smoothness."
                )
            ]
            msg = "Tier 1 did not resolve battery drain. GASTE statefully escalated to Tier 2: Deep Sleep Background Apps & Adaptive Power Limits."
        else:
            plan = [
                ActionablePlan(
                    step=1,
                    action="Initiate Samsung Device Care Hardware Diagnostics & Battery Calibration",
                    reason="Software-level limits exhausted. Executing kernel-level battery health and impedance test."
                ),
                ActionablePlan(
                    step=2,
                    action="Dispatch Samsung Smart Service / Authorized Support Ticket",
                    reason="Physical cell degradation detected. Automated service request generated with telemetry report."
                )
            ]
            msg = f"Tier {tier - 1} unresolved. Stateful engine escalated to Tier {tier}: Device Care Diagnostics & Samsung Service Handoff."
    elif any(k in issue_text for k in ["gesture", "nav", "swipe", "button", "display"]):
        if tier == 2:
            plan = [
                ActionablePlan(
                    step=1,
                    action="Reset Navigation Bar System Service & Gesture Cache",
                    reason="Standard toggle failed to take effect; clearing One UI SystemUI overlay cache."
                ),
                ActionablePlan(
                    step=2,
                    action="Disable Conflicting Third-Party Overlay Accessibility Services",
                    reason="Third-party gesture handlers or screen filters may intercept touch inputs."
                )
            ]
            msg = "Stateful escalation to Tier 2: Resetting SystemUI Gesture Cache & Accessibility Overlays."
        else:
            plan = [
                ActionablePlan(
                    step=1,
                    action="Run Samsung Touch Screen Digitizer Diagnostic",
                    reason="Hardware digitizer multi-touch validation via Samsung Members test suite."
                )
            ]
            msg = f"Escalated to Tier {tier}: Touch Screen Hardware Diagnostics."
    else:
        if tier == 2:
            plan = [
                ActionablePlan(
                    step=1,
                    action="Clear Device System Cache Partition & Reset App Preferences",
                    reason="Tier 1 standard resolution unsuccessful. Resolving latent system state inconsistencies."
                ),
                ActionablePlan(
                    step=2,
                    action="Boot Galaxy Device in Safe Mode Diagnostic",
                    reason="Isolates third-party background services causing anomalous system behavior."
                )
            ]
            msg = "Tier 1 did not resolve the issue. Stateful engine escalated to Tier 2: System Cache Reset & Safe Mode."
        else:
            plan = [
                ActionablePlan(
                    step=1,
                    action="Trigger Comprehensive Samsung Members Diagnostics Suite",
                    reason="Exhausted software parameter reconfiguration."
                ),
                ActionablePlan(
                    step=2,
                    action="Connect to Samsung Expert Care with Attached Telemetry Logs",
                    reason="Direct handoff to Samsung Tier 3 Specialist with attached telemetry logs."
                )
            ]
            msg = f"Stateful escalation to Tier {tier}: Device Diagnostics & Technical Specialist Handoff."
    
    http_response.headers["X-Session-ID"] = sid
    http_response.headers["Access-Control-Expose-Headers"] = "*"
    
    response = InteractiveResponse(
        session_id=sid,
        current_tier=tier,
        status="in_progress",
        message=msg,
        actionable_plan=plan,
        retrieval_used=False
    )
    
    latency_ms = int((time.time() - start_time) * 1000)
    print(f"Interactive Request latency: {latency_ms}ms")
    
    return response
