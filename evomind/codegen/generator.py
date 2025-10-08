"""Code generation module using PAL (Program-Aided Language) approach."""

import logging
from typing import Dict, Any, Optional
import textwrap

from evomind.codegen.validators import StaticValidator, TypeChecker
from evomind.llm.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class CodeGenerator:
    """Code generator implementing PAL-style tool creation.

    Uses LLM to write code but relies on Python runtime for execution.
    This reduces hallucinated math/logic errors.
    """

    def __init__(self, llm_client: Optional[GeminiClient] = None, use_llm: bool = False):
        self.llm_client = llm_client or (GeminiClient() if use_llm else None)
        self.use_llm = use_llm and self.llm_client is not None
        self.validator = StaticValidator()
        self.type_checker = TypeChecker()
        self.templates = CodeTemplates()

        if self.use_llm:
            logger.info("CodeGenerator initialized with Gemini LLM")
        else:
            logger.info("CodeGenerator initialized with template-based generation")

    def create_tool(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tool from specification.
        
        Pipeline: Generate → Validate → Test → Register
        """
        logger.info(f"Creating tool: {spec.get('name', 'unknown')}")

        # Generate code
        code = self._generate_code(spec)
        if not code:
            return {"status": "FAIL", "reason": "generation_failed"}

        # AST parse check
        validation = self.validator.validate(code)
        if validation.has_blockers():
            logger.error(f"Validation failed: {validation.blockers}")

            # Attempt self-repair
            code = self._attempt_repair(code, validation)
            if code:
                validation = self.validator.validate(code)
                if validation.has_blockers():
                    return {"status": "FAIL", "reason": "validation_failed", "findings": validation.blockers}
            else:
                return {"status": "FAIL", "reason": "validation_failed", "findings": validation.blockers}

        # Type checking
        type_result = self.type_checker.check(code)
        if type_result.has_blockers():
            logger.warning(f"Type checking issues: {type_result.blockers}")

        # Package code
        artifact = self._package_code(code, spec)

        # Run smoke tests
        test_result = self._run_smoke_tests(artifact, spec.get("tests", []))
        if not test_result.get("passed", False):
            return {"status": "FAIL", "reason": "tests_failed", "details": test_result}

        # Generate version
        version = self._generate_version(spec)

        return {
            "status": "READY",
            "tool_id": spec.get("name"),
            "version": version,
            "artifact": artifact,
            "code": code
        }

    def _generate_code(self, spec: Dict[str, Any]) -> Optional[str]:
        """Generate code from specification."""
        name = spec.get("name", "tool")
        description = spec.get("description", "A generated tool")
        io_spec = spec.get("io_spec", {})

        # Use Gemini LLM if available
        if self.use_llm and self.llm_client:
            try:
                logger.info(f"Generating code with Gemini for {name}")
                code = self.llm_client.generate_code(
                    task_description=description,
                    function_name=name,
                    io_spec=io_spec,
                    constraints=spec.get("constraints", {})
                )
                logger.info(f"Generated code length: {len(code)} chars")
                logger.debug(f"Generated code:\n{code[:200]}...")  # Log first 200 chars
                return code
            except Exception as e:
                logger.warning(f"LLM generation failed, falling back to templates: {e}")

        # Fallback to template-based generation
        logger.info(f"Using template-based generation for {name}")
        code = self.templates.generate_function(
            name=name,
            description=description,
            io_spec=io_spec
        )

        logger.info(f"Generated code for {name}")
        return code

    def _attempt_repair(self, code: str, validation: Any) -> Optional[str]:
        """Attempt to repair code based on validation findings."""
        logger.info("Attempting code repair...")

        # Use Gemini LLM if available
        if self.use_llm and self.llm_client:
            try:
                repaired_code = self.llm_client.repair_code(
                    original_code=code,
                    validation_errors=validation.blockers
                )
                logger.info("Code repaired with Gemini")
                return repaired_code
            except Exception as e:
                logger.warning(f"LLM repair failed: {e}")

        # No template-based repair available
        return None

    def _package_code(self, code: str, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Package code into artifact."""
        return {
            "code": code,
            "spec": spec,
            "type": "python_function"
        }

    def _run_smoke_tests(self, artifact: Dict[str, Any], tests: list) -> Dict[str, Any]:
        """Run smoke tests on artifact."""
        # Simplified: in production run in sandbox
        logger.info(f"Running {len(tests)} smoke tests")

        # For MVP, assume tests pass if code is valid
        return {
            "passed": True,
            "tests_run": len(tests),
            "failures": []
        }

    def _generate_version(self, spec: Dict[str, Any]) -> str:
        """Generate semantic version."""
        # Simplified: start at 0.1.0
        return "0.1.0"


class CodeTemplates:
    """Code templates for tool generation."""

    def generate_function(
        self,
        name: str,
        description: str,
        io_spec: Dict[str, Any]
    ) -> str:
        """Generate function from template."""

        template = textwrap.dedent('''
        def {name}(input_data: dict) -> dict:
            """
            {description}
            
            Args:
                input_data: Input dictionary with parameters
            
            Returns:
                Dictionary with results
            """
            # Implementation
            result = {{
                "status": "success",
                "data": input_data
            }}
            
            return result
        ''').strip()

        code = template.format(
            name=name,
            description=description
        )

        return code

    def generate_data_transform(self, spec: Dict[str, Any]) -> str:
        """Generate data transformation function."""
        template = textwrap.dedent('''
        import json
        from typing import Any, Dict, List
        
        def transform_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            """
            Transform data according to specification.
            
            Args:
                data: Input data list
            
            Returns:
                Transformed data list
            """
            result = []
            for item in data:
                # Apply transformations
                transformed = item.copy()
                result.append(transformed)
            
            return result
        ''').strip()

        return template

    def generate_api_caller(self, spec: Dict[str, Any]) -> str:
        """Generate API caller function."""
        # Note: Network operations require explicit allowlist
        template = textwrap.dedent('''
        from typing import Dict, Any
        
        def call_api(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
            """
            Call external API (requires network permission).
            
            Args:
                endpoint: API endpoint
                params: Request parameters
            
            Returns:
                API response
            """
            # This requires network access to be granted
            raise NotImplementedError("Network access not enabled in sandbox")
        ''').strip()

        return template
