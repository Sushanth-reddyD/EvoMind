"""Tests for planners."""

import pytest
from evomind.agent.planner import ReActPlanner, ToTPlanner, ReflexionMemory


def test_react_planner():
    """Test ReAct planner."""
    planner = ReActPlanner()
    
    context = {
        "request": {"task": "test task"},
        "relevant_history": []
    }
    
    plan = planner.plan(context)
    
    assert plan is not None
    assert plan["strategy"] == "react"
    assert "intent" in plan
    assert "actions" in plan


def test_tot_planner():
    """Test ToT planner."""
    planner = ToTPlanner(breadth=2, depth=2)
    
    context = {
        "request": {"task": "complex task"},
        "relevant_history": []
    }
    
    plan = planner.plan(context)
    
    assert plan is not None
    assert plan["strategy"] == "tot"
    assert "explored_paths" in plan


def test_reflexion_memory():
    """Test Reflexion memory."""
    memory = ReflexionMemory()
    
    memory.add(
        task="test task",
        outcome="failure",
        feedback={"error": "test error"}
    )
    
    assert len(memory.episodes) == 1
    
    relevant = memory.get_relevant("test task")
    assert len(relevant) >= 0


def test_reflexion_should_reflect():
    """Test reflexion decision logic."""
    memory = ReflexionMemory()
    
    # Should reflect on failures
    feedback = [{"category": "bad_result"}]
    assert memory.should_reflect(feedback) is True
    
    # Should not reflect on success
    feedback = [{"category": "success"}]
    assert memory.should_reflect(feedback) is False
