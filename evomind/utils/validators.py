"""Result validation utilities."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ResultValidator:
    """Validator for execution results."""

    def validate_result(
        self,
        result: Dict[str, Any],
        criteria: Dict[str, Any]
    ) -> bool:
        """Validate result against success criteria.
        
        Args:
            result: Execution result
            criteria: Success criteria
        
        Returns:
            True if validation passes
        """
        if not result:
            return False

        # Check basic criteria
        has_result = criteria.get("has_result", True)
        if has_result and "result" not in result:
            logger.warning("Result missing required 'result' field")
            return False

        no_errors = criteria.get("no_errors", True)
        if no_errors:
            if result.get("status") == "error":
                logger.warning("Result has error status")
                return False

            if "error" in result:
                logger.warning("Result contains error")
                return False

        # Check schema validation
        valid_schema = criteria.get("valid_schema", True)
        if valid_schema:
            if not self._validate_schema(result, criteria.get("schema", {})):
                logger.warning("Result schema validation failed")
                return False

        return True

    def _validate_schema(self, result: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate result against schema."""
        if not schema:
            return True

        # Simplified schema validation
        # In production: use jsonschema or pydantic

        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in result:
                logger.warning(f"Required field '{field}' missing from result")
                return False

        return True


class InputValidator:
    """Validator for input data."""

    @staticmethod
    def validate_size(data: Any, max_size_mb: int = 10) -> bool:
        """Validate data size."""
        import sys
        size_bytes = sys.getsizeof(data)
        size_mb = size_bytes / (1024 * 1024)

        if size_mb > max_size_mb:
            logger.warning(f"Input data too large: {size_mb:.2f}MB > {max_size_mb}MB")
            return False

        return True

    @staticmethod
    def sanitize_output(data: Any) -> Any:
        """Sanitize output data."""
        # Remove sensitive patterns
        if isinstance(data, dict):
            return {k: InputValidator.sanitize_output(v) for k, v in data.items()}
        elif isinstance(data, str):
            # Simplified: in production use proper secret detection
            if "password" in data.lower() or "secret" in data.lower():
                return "[REDACTED]"

        return data
