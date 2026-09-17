from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class BaseDeeplink(BaseModel):
    deeplink: str

class Deeplink(BaseDeeplink):
    description: str
    message: Optional[str] = ""
    classes: Optional[Dict[str, str]] = None
    originalType: Optional[str] = None

class Condition(str, Enum):
    greater = "greater"
    equal = "equal"
    less = "less"

class ResultTypes(str, Enum):
    boolean = "boolean"
    intNum = "integer"
    string = "str"
    floatNum = "float"

class actionCategory(str, Enum):
    auto = "auto"
    manual = "manual"
    critical = "critical"

class ValidationDeepLink(BaseDeeplink):
    key: str
    resultType: Optional[ResultTypes] = None
    condition: Optional[Condition] = None
    value: Optional[str] = None

class StepGroup(BaseModel):
    steps: List[str]
    validationDeeplink: Optional[ValidationDeepLink] = None
    actionableDeeplink: Optional[Deeplink] = None

class Action(BaseModel):
    actionName: str
    description: str
    stepGroups: List[StepGroup]
    category: Optional[actionCategory] = actionCategory.manual

class Goal(BaseModel):
    goal: str
    title: str
    actions: List[Action]
    score: float

class ContextDeeplinkResponse(BaseModel):
    """RAG response containing a list of Goal objects."""
    contexts: List[Goal] = []

# Request Models
class TroubleshootRequest(BaseModel):
    query: str
    siis_response: Optional[str] = None

class InteractiveRequest(BaseModel):
    query: str

class ActionablePlan(BaseModel):
    step: int
    action: str
    reason: str

class InteractiveResponse(BaseModel):
    session_id: str
    current_tier: int
    status: str
    message: str
    actionable_plan: List[ActionablePlan]
    retrieval_used: bool
