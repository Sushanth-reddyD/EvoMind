"""Google Gemini LLM client wrapper."""

import logging
import os
from typing import Dict, Any, Optional, List
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class GeminiClient:
    """Wrapper for Google Gemini API.

    Uses the google-genai library to interact with Gemini models.
    API key is read from GEMINI_API_KEY environment variable.
    """

    def __init__(
        self,
        model: str = "gemini-2.0-flash-exp",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """Initialize Gemini client.

        Args:
            model: Gemini model name (default: gemini-2.0-flash-exp)
            api_key: API key (reads from GEMINI_API_KEY env var if not provided)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize client - API key from environment
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            # Client will try to get key from environment
            self.client = genai.Client()

        logger.info(f"Initialized Gemini client with model: {model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate content using Gemini.

        Args:
            prompt: The prompt to send to Gemini
            system_instruction: Optional system instruction
            **kwargs: Additional parameters to pass to the API

        Returns:
            Generated text response

        Raises:
            Exception: If API call fails after retries
        """
        try:
            # Build config
            config = {
                "temperature": kwargs.get("temperature", self.temperature),
                "max_output_tokens": kwargs.get("max_tokens", self.max_tokens),
            }

            # Add system instruction if provided
            contents = prompt
            if system_instruction:
                config["system_instruction"] = system_instruction

            # Call Gemini API
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )

            logger.debug(f"Gemini API call successful")
            return response.text

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    def generate_code(
        self,
        task_description: str,
        function_name: str,
        io_spec: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate Python code for a specific task.

        Args:
            task_description: Description of what the code should do
            function_name: Name of the function to generate
            io_spec: Input/output specification
            constraints: Optional constraints (timeout, memory, etc.)

        Returns:
            Generated Python code
        """
        system_instruction = """You are an expert Python code generator.
Generate clean, efficient, well-documented Python code.
Follow PEP 8 style guidelines and Python 3.10+ best practices.

CRITICAL RULES:
- Use lowercase built-in types: list, dict, tuple, set (NOT List, Dict, Tuple, Set from typing)
- For type hints: list[int], dict[str, str], etc. (Python 3.10+ syntax)
- NEVER instantiate type objects: NO List(), Dict(), Set() - use list(), dict(), set()
- Only import from typing if you need Union, Optional, Any
- Return ONLY the function code - no explanations, no markdown, no ``` blocks
Do NOT wrap the code in ```python or ``` markers."""

        prompt = f"""Generate a Python function with the following specifications:

Function Name: {function_name}
Description: {task_description}

Input Specification:
{io_spec.get('input', 'dict with parameters')}

Output Specification:
{io_spec.get('output', 'dict with results')}

Requirements:
- Include comprehensive docstring
- Use modern Python 3.10+ type hints: list[int], dict[str, any] (NOT List, Dict from typing module)
- NEVER use List(), Dict(), Set(), Tuple() - always use list(), dict(), set(), tuple()
- Handle errors gracefully with try/except
- Return a dictionary with 'status' and 'result' keys
{"- Must complete within " + str(constraints.get('timeout', 30)) + " seconds" if constraints else ""}
{"- Memory usage under " + str(constraints.get('memory_mb', 512)) + "MB" if constraints else ""}
- Do NOT use network imports (requests, urllib, socket) - they will be blocked
- Only use safe built-in modules: json, math, re, datetime, collections, itertools

Return ONLY the Python function code. No markdown, no explanations, no ```python blocks."""

        response = self.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.3  # Lower temperature for code generation
        )
        
        # Clean up the response - remove markdown code blocks if present
        code = self._clean_code_response(response)
        return code
    
    def _clean_code_response(self, response: str) -> str:
        """Clean code response by removing markdown and extra text.
        
        Args:
            response: Raw response from LLM
            
        Returns:
            Cleaned Python code
        """
        # Remove leading/trailing whitespace
        code = response.strip()
        
        # Remove markdown code blocks
        if code.startswith("```python"):
            code = code[len("```python"):].strip()
        elif code.startswith("```"):
            code = code[3:].strip()
        
        if code.endswith("```"):
            code = code[:-3].strip()
        
        # Remove any explanatory text before the function
        lines = code.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('def ') or line.strip().startswith('import ') or line.strip().startswith('from '):
                start_idx = i
                break
        
        if start_idx > 0:
            code = '\n'.join(lines[start_idx:])
        
        return code.strip()

    def generate_plan(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate execution plan for a task.

        Args:
            task: Task description
            context: Additional context

        Returns:
            Plan dictionary with intent, actions, success criteria
        """
        system_instruction = """You are an AI planning assistant.
Analyze tasks and create structured execution plans.
Be concise and practical.
Return JSON format only."""

        prompt = f"""Analyze this task and create an execution plan:

Task: {task}

Context:
{context}

Generate a JSON plan with:
{{
    "intent": "clear task intent",
    "io_spec": {{
        "input_type": "type of input",
        "output_type": "expected output type"
    }},
    "actions": [
        {{"type": "action_type", "description": "what to do"}}
    ],
    "success_criteria": {{
        "has_result": true,
        "no_errors": true
    }},
    "confidence": 0.0-1.0
}}

Return ONLY valid JSON, no explanations."""

        response = self.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.5
        )

        # Parse JSON response
        import json
        try:
            # Try to extract JSON from response
            response_clean = response.strip()
            if response_clean.startswith("```"):
                # Remove markdown code blocks
                lines = response_clean.split("\n")
                response_clean = "\n".join(lines[1:-1])
            return json.loads(response_clean)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse plan JSON: {response}")
            # Return fallback plan
            return {
                "intent": task,
                "io_spec": {"input_type": "generic", "output_type": "generic"},
                "actions": [{"type": "execute", "description": task}],
                "success_criteria": {"has_result": True, "no_errors": True},
                "confidence": 0.5
            }

    def repair_code(
        self,
        original_code: str,
        validation_errors: List[Dict[str, Any]]
    ) -> str:
        """Repair code based on validation errors.

        Args:
            original_code: The code that failed validation
            validation_errors: List of validation errors

        Returns:
            Repaired code
        """
        system_instruction = """You are a Python code repair expert.
Fix validation errors while preserving functionality.
IMPORTANT: Return ONLY the corrected Python code without any markdown formatting, explanations, or code blocks.
Do NOT wrap the code in ```python or ``` markers."""

        errors_text = "\n".join([
            f"- Line {err.get('line', '?')}: {err.get('category', 'error')} - {err.get('message', 'unknown error')}"
            for err in validation_errors
        ])

        prompt = f"""Fix the following Python code to resolve these validation errors:

ERRORS:
{errors_text}

ORIGINAL CODE:
{original_code}

INSTRUCTIONS:
1. Fix all syntax errors
2. Preserve the original function name and logic
3. Maintain proper indentation
4. Keep all docstrings and type hints

Return ONLY the corrected Python code. No markdown, no explanations, no ```python blocks."""

        response = self.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.1  # Very low temperature for repairs
        )
        
        # Clean the response
        return self._clean_code_response(response)

    def chat(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Simple chat interface.

        Args:
            message: User message
            conversation_history: Previous conversation turns

        Returns:
            Assistant response
        """
        system_instruction = """You are EvoMind, an AI coding assistant.
Help users with code generation, planning, and problem-solving.
Be helpful, concise, and technical."""

        # Build prompt with history
        if conversation_history:
            history_text = "\n".join([
                f"{turn['role']}: {turn['content']}"
                for turn in conversation_history
            ])
            prompt = f"{history_text}\nuser: {message}\nassistant:"
        else:
            prompt = message

        return self.generate_content(
            prompt=prompt,
            system_instruction=system_instruction
        )
