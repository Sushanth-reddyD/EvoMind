"""Static code validation using AST, policy gates, SAST, and type checking."""

import ast
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of static validation."""

    def __init__(self):
        self.passed: bool = True
        self.findings: List[Dict[str, Any]] = []
        self.blockers: List[Dict[str, Any]] = []

    def add_finding(self, severity: str, category: str, message: str, line: Optional[int] = None) -> None:
        """Add validation finding."""
        finding = {
            "severity": severity,
            "category": category,
            "message": message,
            "line": line
        }
        self.findings.append(finding)

        if severity in ["critical", "high"]:
            self.blockers.append(finding)
            self.passed = False

    def has_blockers(self) -> bool:
        """Check if there are blocking issues."""
        return len(self.blockers) > 0


class StaticValidator:
    """Static code validator implementing multiple validation layers."""

    def __init__(self, allow_network: bool = False):
        """Initialize validator.
        
        Args:
            allow_network: If True, allows network-related imports (urllib, requests, socket)
        """
        self.allow_network = allow_network
        
        # Always dangerous - never allow
        self.always_dangerous = {
            "os",
            "subprocess",
            "ctypes",
            "multiprocessing",
            "threading",
            "__import__",
            "eval",
            "exec",
            "compile"
        }
        
        # Network modules - conditionally allowed
        self.network_imports = {
            "socket",
            "http",
            "urllib",
            "requests",
            "httpx"
        }
        
        # Build dangerous imports list based on network permission
        if allow_network:
            self.dangerous_imports = self.always_dangerous.copy()
            logger.info("Network access enabled for validation")
        else:
            self.dangerous_imports = self.always_dangerous | self.network_imports

        self.allowed_imports = {
            "json",
            "re",
            "math",
            "datetime",
            "typing",
            "dataclasses",
            "collections",
            "itertools",
            "functools",
            "string",
            "statistics",
            "decimal",
            "fractions"
        }
        
        # Add network imports to allowed if network is enabled
        if allow_network:
            self.allowed_imports |= self.network_imports

    def validate(self, code: str) -> ValidationResult:
        """Run all validation checks."""
        result = ValidationResult()

        # AST parse check
        if not self._validate_ast(code, result):
            return result

        # Policy gate check
        self._validate_policy(code, result)

        # SAST-like checks
        self._validate_security(code, result)

        # Additional safety checks
        self._validate_safety(code, result)

        return result

    def _validate_ast(self, code: str, result: ValidationResult) -> bool:
        """Validate AST parseability."""
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            result.add_finding(
                "critical",
                "syntax",
                f"Syntax error: {e.msg}",
                e.lineno
            )
            return False

    def _validate_policy(self, code: str, result: ValidationResult) -> None:
        """Validate against policy rules."""
        try:
            tree = ast.parse(code)

            # Check imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._check_import(alias.name, result, node.lineno)

                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._check_import(node.module, result, node.lineno)

                # Check for dangerous calls
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ["eval", "exec", "compile", "__import__"]:
                            result.add_finding(
                                "critical",
                                "policy",
                                f"Forbidden function call: {node.func.id}",
                                node.lineno
                            )

        except Exception as e:
            logger.error(f"Policy validation error: {e}")
            result.add_finding("high", "policy", f"Policy check failed: {e}")

    def _check_import(self, module: str, result: ValidationResult, line: int) -> None:
        """Check if import is allowed."""
        base_module = module.split(".")[0]

        if base_module in self.dangerous_imports:
            result.add_finding(
                "critical",
                "policy",
                f"Forbidden import: {module}",
                line
            )
        elif base_module not in self.allowed_imports:
            result.add_finding(
                "medium",
                "policy",
                f"Import requires review: {module}",
                line
            )

    def _validate_security(self, code: str, result: ValidationResult) -> None:
        """SAST-like security checks."""
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                # Check for file operations
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ["open", "file"]:
                            result.add_finding(
                                "high",
                                "security",
                                "File operations detected - ensure proper sandboxing",
                                node.lineno
                            )

                # Check for network operations
                if isinstance(node, ast.Attribute):
                    if node.attr in ["urlopen", "get", "post", "request"]:
                        result.add_finding(
                            "high",
                            "security",
                            "Network operation detected",
                            node.lineno
                        )

        except Exception as e:
            logger.error(f"Security validation error: {e}")

    def _validate_safety(self, code: str, result: ValidationResult) -> None:
        """Additional safety checks."""
        # Check code length
        if len(code) > 10000:
            result.add_finding(
                "medium",
                "safety",
                "Code is very long, may indicate complexity issues"
            )

        # Check for infinite loop patterns (simplified)
        if "while True:" in code and "break" not in code:
            result.add_finding(
                "high",
                "safety",
                "Potential infinite loop detected"
            )


class TypeChecker:
    """Type checking wrapper (simplified)."""

    def check(self, code: str) -> ValidationResult:
        """Run type checking."""
        result = ValidationResult()

        # In production: integrate mypy or pyright
        # For now, just validate that type hints are present
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

            for func in functions:
                if not func.returns:
                    result.add_finding(
                        "low",
                        "types",
                        f"Function '{func.name}' missing return type hint",
                        func.lineno
                    )

        except Exception as e:
            logger.error(f"Type checking error: {e}")

        return result
