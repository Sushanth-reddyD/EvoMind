"""Tests for sandbox executor."""

from evomind.sandbox.executor import SandboxExecutor
from evomind.sandbox.policies import SandboxPolicy, ResourcePolicy, SecurityPolicy


def test_sandbox_initialization():
    """Test sandbox executor initialization."""
    executor = SandboxExecutor()
    
    assert executor is not None


def test_resource_policy():
    """Test resource policy creation."""
    policy = ResourcePolicy(
        cpu_time_limit=10,
        memory_limit_mb=256
    )
    
    assert policy.cpu_time_limit == 10
    assert policy.memory_limit_mb == 256


def test_security_policy():
    """Test security policy creation."""
    policy = SecurityPolicy(
        network_enabled=False,
        filesystem_readonly=True
    )
    
    assert policy.network_enabled is False
    assert policy.filesystem_readonly is True


def test_execute_simple_tool():
    """Test executing a simple tool."""
    executor = SandboxExecutor()
    
    tool = {
        "tool_id": "test_tool",
        "code": """
def test_tool(input_data):
    return {"status": "success", "result": input_data}
"""
    }
    
    args = {"test": "data"}
    
    result = executor.execute(tool, args)
    
    assert result is not None
    assert "status" in result


def test_sandbox_policy_combination():
    """Test combining resource and security policies."""
    policy = SandboxPolicy(
        resource=ResourcePolicy(cpu_time_limit=5),
        security=SecurityPolicy(network_enabled=False)
    )
    
    assert policy.resource.cpu_time_limit == 5
    assert policy.security.network_enabled is False
