"""Agent state management and state machine."""

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class StateType(str, Enum):
    """Agent state types."""
    IDLE = "idle"
    PLAN = "plan"
    SELECT_TOOL = "select_tool"
    DESIGN_TOOL = "design_tool"
    VALIDATE = "validate"
    EXECUTE = "execute"
    VERIFY = "verify"
    RESPOND = "respond"
    LEARN = "learn"
    ERROR = "error"


@dataclass
class StateTransition:
    """Represents a state transition."""
    from_state: StateType
    to_state: StateType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """Agent state container."""
    current_state: StateType = StateType.IDLE
    request: Optional[Dict[str, Any]] = None
    plan: Optional[Dict[str, Any]] = None
    selected_tool: Optional[str] = None
    execution_result: Optional[Any] = None
    feedback: List[Dict[str, Any]] = field(default_factory=list)
    history: List[StateTransition] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    
    def transition(self, to_state: StateType, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Transition to a new state."""
        transition = StateTransition(
            from_state=self.current_state,
            to_state=to_state,
            metadata=metadata or {}
        )
        self.history.append(transition)
        self.current_state = to_state
    
    def add_feedback(self, category: str, details: Dict[str, Any]) -> None:
        """Add feedback entry."""
        self.feedback.append({
            "category": category,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def can_retry(self) -> bool:
        """Check if retry is allowed."""
        return self.retry_count < self.max_retries
    
    def increment_retry(self) -> None:
        """Increment retry counter."""
        self.retry_count += 1
    
    def reset(self) -> None:
        """Reset state for new request."""
        self.current_state = StateType.IDLE
        self.request = None
        self.plan = None
        self.selected_tool = None
        self.execution_result = None
        self.feedback = []
        self.retry_count = 0


class ContextManager:
    """Manages agent context including short-term and long-term memory."""
    
    def __init__(self):
        self.short_term: Dict[str, Any] = {}
        self.long_term: Dict[str, Any] = {}
        self.episodic: List[Dict[str, Any]] = []
    
    def build(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Build context from request."""
        return {
            "request": request,
            "short_term": self.short_term,
            "relevant_history": self._get_relevant_history(request)
        }
    
    def _get_relevant_history(self, request: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Retrieve relevant historical context."""
        # Simplified: return recent episodic memories
        return self.episodic[-5:] if self.episodic else []
    
    def update_short_term(self, key: str, value: Any) -> None:
        """Update short-term memory."""
        self.short_term[key] = value
    
    def add_episodic(self, episode: Dict[str, Any]) -> None:
        """Add episodic memory."""
        episode["timestamp"] = datetime.utcnow().isoformat()
        self.episodic.append(episode)
    
    def clear_short_term(self) -> None:
        """Clear short-term memory."""
        self.short_term.clear()
