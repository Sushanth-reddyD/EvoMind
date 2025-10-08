"""Tests for code generation."""

import pytest
from evomind.codegen.generator import CodeGenerator
from evomind.codegen.validators import StaticValidator


def test_code_generator_initialization():
    """Test code generator initialization."""
    generator = CodeGenerator()
    
    assert generator is not None


def test_create_tool():
    """Test tool creation."""
    generator = CodeGenerator()
    
    spec = {
        "name": "test_tool",
        "description": "A test tool",
        "io_spec": {},
        "constraints": {},
        "tests": []
    }
    
    result = generator.create_tool(spec)
    
    assert result is not None
    assert "status" in result


def test_static_validation_valid_code():
    """Test static validation with valid code."""
    validator = StaticValidator()
    
    code = """
def test_function(x: int) -> int:
    return x * 2
"""
    
    result = validator.validate(code)
    
    assert result.passed is True
    assert len(result.blockers) == 0


def test_static_validation_syntax_error():
    """Test static validation with syntax error."""
    validator = StaticValidator()
    
    code = "def invalid syntax here"
    
    result = validator.validate(code)
    
    assert result.passed is False
    assert len(result.blockers) > 0


def test_static_validation_forbidden_import():
    """Test static validation catches forbidden imports."""
    validator = StaticValidator()
    
    code = """
import subprocess
import os

def dangerous():
    subprocess.call(['ls'])
"""
    
    result = validator.validate(code)
    
    assert result.passed is False
    assert any(f["category"] == "policy" for f in result.blockers)


def test_template_generation():
    """Test template-based code generation."""
    from evomind.codegen.generator import CodeTemplates
    
    templates = CodeTemplates()
    
    code = templates.generate_function(
        name="test_func",
        description="Test function",
        io_spec={}
    )
    
    assert code is not None
    assert "def test_func" in code
