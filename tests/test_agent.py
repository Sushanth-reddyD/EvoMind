"""Tests for agent controller."""

import pytest
from evomind.agent.controller import AgentController
from evomind.agent.state import AgentState, StateType


def test_agent_initialization():
    """Test agent controller initialization."""
    agent = AgentController()
    
    assert agent is not None
    assert agent.state.current_state == StateType.IDLE


def test_handle_simple_request():
    """Test handling a simple request."""
    agent = AgentController()
    
    request = {
        "task": "simple test task"
    }
    
    result = agent.handle_request(request)
    
    assert result is not None
    assert "status" in result


def test_state_transitions():
    """Test state machine transitions."""
    state = AgentState()
    
    assert state.current_state == StateType.IDLE
    
    state.transition(StateType.PLAN)
    assert state.current_state == StateType.PLAN
    assert len(state.history) == 1
    
    state.transition(StateType.EXECUTE)
    assert state.current_state == StateType.EXECUTE
    assert len(state.history) == 2


def test_feedback_tracking():
    """Test feedback tracking."""
    state = AgentState()
    
    state.add_feedback("error", {"message": "test error"})
    
    assert len(state.feedback) == 1
    assert state.feedback[0]["category"] == "error"


def test_retry_logic():
    """Test retry logic."""
    state = AgentState()
    
    assert state.can_retry() is True
    
    state.increment_retry()
    assert state.retry_count == 1
    
    state.increment_retry()
    state.increment_retry()
    assert state.can_retry() is False
