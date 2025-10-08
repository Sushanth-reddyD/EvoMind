"""Main agent controller orchestrating the AI agent system."""

from typing import Any, Dict, Optional
import logging

from evomind.agent.state import AgentState, StateType, ContextManager
from evomind.agent.planner import ReActPlanner, ToTPlanner, ReflexionMemory
from evomind.registry.tool_registry import ToolRegistry
from evomind.codegen.generator import CodeGenerator
from evomind.sandbox.executor import SandboxExecutor
from evomind.utils.validators import ResultValidator

logger = logging.getLogger(__name__)


class AgentController:
    """Main agent controller implementing the core decision loop.
    
    State machine: Idle → Plan → SelectTool/DesignTool → Validate → Execute → Verify → Respond → Learn
    """

    def __init__(
        self,
        tool_registry: Optional[ToolRegistry] = None,
        code_generator: Optional[CodeGenerator] = None,
        sandbox_executor: Optional[SandboxExecutor] = None,
        confidence_threshold: float = 0.7
    ):
        self.tool_registry = tool_registry or ToolRegistry()
        self.code_generator = code_generator or CodeGenerator()
        self.sandbox_executor = sandbox_executor or SandboxExecutor()
        self.confidence_threshold = confidence_threshold

        self.react_planner = ReActPlanner()
        self.tot_planner = ToTPlanner()
        self.reflexion = ReflexionMemory()
        self.context_manager = ContextManager()
        self.validator = ResultValidator()

        self.state = AgentState()

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming request.
        
        Main entry point implementing the agent decision loop.
        """
        logger.info(f"Handling request: {request.get('task', 'unknown')}")

        # Prevent infinite recursion
        if self.state.retry_count >= self.state.max_retries:
            return self._graceful_degrade(self.state.feedback)

        # Only reset on first attempt
        if self.state.retry_count == 0:
            self.state.reset()

        self.state.request = request
        self.state.transition(StateType.PLAN)

        try:
            # Build context
            ctx = self.context_manager.build(request)

            # Plan
            plan = self._plan(ctx)
            self.state.plan = plan

            # Search for existing tools
            candidate_tools = self.tool_registry.search(
                plan.get("intent", ""),
                plan.get("io_spec", {})
            )

            # Decide: use existing or create new tool
            if self._match_found(candidate_tools, plan):
                self.state.transition(StateType.SELECT_TOOL)
                tool = self._rank_and_select(candidate_tools, plan)
                self.state.selected_tool = tool.get("id")

                # Execute existing tool
                result = self._execute_tool(tool, plan)

            else:
                self.state.transition(StateType.DESIGN_TOOL)
                # Create new tool
                tool_spec = self._synthesize_tool_spec(plan)
                tool = self._create_tool(tool_spec)

                if tool.get("status") == "READY":
                    self.state.selected_tool = tool.get("tool_id")
                    result = self._execute_tool(tool, plan)
                else:
                    self.state.add_feedback("tool_creation_failed", tool)
                    result = None

            # Validate result
            self.state.transition(StateType.VERIFY)
            if result and self.validator.validate_result(result, plan.get("success_criteria", {})):
                self.state.execution_result = result
                self.state.transition(StateType.RESPOND)
                return self._respond(result)
            else:
                self.state.add_feedback("bad_result", {"result": result})

                # Handle failures with reflexion
                if self.reflexion.should_reflect(self.state.feedback):
                    self.state.transition(StateType.LEARN)
                    self._learn_from_feedback()

                    if self.state.can_retry():
                        self.state.increment_retry()
                        logger.info(f"Retrying request (attempt {self.state.retry_count})")
                        return self.handle_request(request)

            # Graceful degradation
            return self._graceful_degrade(self.state.feedback)

        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            self.state.transition(StateType.ERROR)
            return {
                "status": "error",
                "error": str(e),
                "message": "An unexpected error occurred"
            }

    def _plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate execution plan."""
        # Use ReAct by default, escalate to ToT for low confidence
        plan = self.react_planner.plan(context)

        if plan.get("confidence", 0) < self.confidence_threshold:
            logger.info("Low confidence, escalating to ToT planner")
            plan = self.tot_planner.plan(context)

        return plan

    def _match_found(self, candidates: list, plan: Dict[str, Any]) -> bool:
        """Check if suitable tool exists."""
        return len(candidates) > 0

    def _rank_and_select(self, candidates: list, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Rank and select best tool."""
        # Simplified: select first candidate
        # In production: use semantic similarity, usage stats, version stability
        if not candidates:
            return {}
        return candidates[0]

    def _synthesize_tool_spec(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize tool specification from plan."""
        return {
            "name": f"tool_{plan.get('intent', 'generic').replace(' ', '_')}",
            "description": plan.get("intent", ""),
            "io_spec": plan.get("io_spec", {}),
            "constraints": {
                "timeout": 30,
                "memory_mb": 512,
                "no_network": True
            },
            "tests": self._generate_test_stub(plan)
        }

    def _generate_test_stub(self, plan: Dict[str, Any]) -> list:
        """Generate test cases stub."""
        return [
            {"name": "test_basic", "input": {}, "expected": "success"}
        ]

    def _create_tool(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create new tool from specification."""
        self.state.transition(StateType.VALIDATE)
        result = self.code_generator.create_tool(spec)
        return result

    def _execute_tool(self, tool: Dict[str, Any], plan: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute tool in sandbox."""
        self.state.transition(StateType.EXECUTE)

        try:
            args = plan.get("args", {})
            result = self.sandbox_executor.execute(tool, args)
            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            self.state.add_feedback("execution_error", {"error": str(e)})
            return None

    def _learn_from_feedback(self) -> None:
        """Learn from feedback using Reflexion."""
        task = self.state.request.get("task", "")
        feedback_summary = {
            "errors": [f for f in self.state.feedback if f.get("category") in ["error", "bad_result"]],
            "count": len(self.state.feedback)
        }

        self.reflexion.add(task, "failure", feedback_summary)

        # Store in episodic memory
        self.context_manager.add_episodic({
            "task": task,
            "outcome": "failure",
            "feedback": self.state.feedback
        })

    def _respond(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format successful response."""
        return {
            "status": "success",
            "result": result,
            "tool_used": self.state.selected_tool,
            "metadata": {
                "retries": self.state.retry_count,
                "state_history": [s.to_state.value for s in self.state.history]
            }
        }

    def _graceful_degrade(self, feedback: list) -> Dict[str, Any]:
        """Gracefully degrade on failure."""
        return {
            "status": "degraded",
            "message": "Unable to complete request fully",
            "feedback": feedback,
            "partial_result": self.state.execution_result
        }
