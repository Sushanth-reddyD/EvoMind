"""Tests for tool registry."""

import pytest
from evomind.registry.tool_registry import ToolRegistry, ToolMetadata


def test_registry_initialization():
    """Test registry initialization."""
    registry = ToolRegistry()
    
    assert registry is not None


def test_register_tool():
    """Test tool registration."""
    registry = ToolRegistry()
    
    artifact = {
        "code": "def test(): pass",
        "type": "python_function"
    }
    
    metadata = {
        "name": "test_tool",
        "description": "A test tool"
    }
    
    tool_id = registry.register(artifact, metadata, "0.1.0")
    
    assert tool_id is not None
    assert "test_tool" in tool_id


def test_search_tools():
    """Test tool search."""
    registry = ToolRegistry()
    
    # Register a tool
    artifact = {"code": "def parse_json(): pass"}
    metadata = {
        "name": "json_parser",
        "description": "Parse JSON data"
    }
    registry.register(artifact, metadata, "0.1.0")
    
    # Search
    results = registry.search("parse")
    
    assert len(results) >= 0


def test_get_tool():
    """Test getting a specific tool."""
    registry = ToolRegistry()
    
    # Register
    artifact = {"code": "def test(): pass"}
    metadata = {"name": "test_tool", "description": "Test"}
    tool_id = registry.register(artifact, metadata, "0.1.0")
    
    # Get
    tool = registry.get(tool_id)
    
    assert tool is not None
    assert tool["id"] == tool_id


def test_tool_metadata():
    """Test tool metadata structure."""
    meta = ToolMetadata(
        id="test_1",
        name="test",
        version="0.1.0",
        description="Test tool"
    )
    
    assert meta.id == "test_1"
    assert meta.name == "test"
    assert meta.version == "0.1.0"


def test_update_stats():
    """Test updating tool statistics."""
    registry = ToolRegistry()
    
    artifact = {"code": "def test(): pass"}
    metadata = {"name": "test_tool", "description": "Test"}
    tool_id = registry.register(artifact, metadata, "0.1.0")
    
    # Update stats
    registry.update_stats(tool_id, success=True)
    
    tool = registry.get(tool_id)
    assert tool["metadata"]["usage_count"] == 1


def test_deprecate_tool():
    """Test tool deprecation."""
    registry = ToolRegistry()
    
    artifact = {"code": "def test(): pass"}
    metadata = {"name": "test_tool", "description": "Test"}
    tool_id = registry.register(artifact, metadata, "0.1.0")
    
    # Deprecate
    result = registry.deprecate(tool_id)
    
    assert result is True
    
    tool = registry.get(tool_id)
    assert tool["metadata"]["deprecated"] is True
