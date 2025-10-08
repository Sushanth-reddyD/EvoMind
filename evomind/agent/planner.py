"""Planning modules for agent decision-making."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

from evomind.llm.gemini_client import GeminiClient

logger = logging.getLogger(__name__)


class Planner(ABC):
    """Base planner interface."""

    @abstractmethod
    def plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a plan from context."""
        pass


class ReActPlanner(Planner):
    """ReAct (Reasoning + Acting) planner.

    Interleaves thinking and acting: thought → action → observation.
    This is the default planner for most tasks.
    """

    def __init__(self, llm_client: Optional[GeminiClient] = None, use_llm: bool = False):
        self.llm_client = llm_client or (GeminiClient() if use_llm else None)
        self.use_llm = use_llm and self.llm_client is not None

        if self.use_llm:
            logger.info("ReActPlanner initialized with Gemini LLM")
        else:
            logger.info("ReActPlanner initialized with rule-based planning")

    def plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ReAct plan."""
        request = context.get("request", {})
        task = request.get("task", "")

        # Use Gemini LLM if available
        if self.use_llm and self.llm_client:
            try:
                logger.info("Generating plan with Gemini")
                plan = self.llm_client.generate_plan(task, context)
                plan["strategy"] = "react"
                return plan
            except Exception as e:
                logger.warning(f"LLM planning failed, using rule-based: {e}")

        # Fallback to rule-based planning
        plan = {
            "strategy": "react",
            "intent": self._extract_intent(task),
            "io_spec": self._infer_io_spec(task),
            "actions": self._generate_actions(task, context),
            "success_criteria": self._define_success_criteria(task),
            "confidence": self._estimate_confidence(task, context)
        }

        logger.info(f"Generated ReAct plan with confidence: {plan['confidence']}")
        return plan

    def _extract_intent(self, task: str) -> str:
        """Extract task intent."""
        # Simplified: in production, use LLM
        return task.lower().strip()

    def _infer_io_spec(self, task: str) -> Dict[str, Any]:
        """Infer input/output specification."""
        return {
            "input_type": "generic",
            "output_type": "generic",
            "constraints": []
        }

    def _generate_actions(self, task: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate action sequence."""
        return [
            {"type": "search_tools", "query": task},
            {"type": "execute_or_create", "depends_on": "search_tools"}
        ]

    def _define_success_criteria(self, task: str) -> Dict[str, Any]:
        """Define success criteria."""
        return {
            "has_result": True,
            "no_errors": True,
            "valid_schema": True
        }

    def _estimate_confidence(self, task: str, context: Dict[str, Any]) -> float:
        """Estimate confidence in plan."""
        # Simplified heuristic
        has_history = len(context.get("relevant_history", [])) > 0
        return 0.8 if has_history else 0.6


class ToTPlanner(Planner):
    """Tree of Thoughts planner.
    
    Uses exploration of multiple reasoning paths for complex tasks.
    More expensive than ReAct, use only for hard tasks.
    """

    def __init__(self, llm_client: Optional[Any] = None, breadth: int = 3, depth: int = 2):
        self.llm_client = llm_client
        self.breadth = breadth
        self.depth = depth

    def plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ToT plan with exploration."""
        request = context.get("request", {})
        task = request.get("task", "")

        # Generate multiple candidate approaches
        candidates = self._generate_candidates(task, context)

        # Evaluate and select best path
        best_path = self._select_best_path(candidates, context)

        plan = {
            "strategy": "tot",
            "intent": task.lower().strip(),
            "io_spec": self._infer_io_spec(task),
            "actions": best_path.get("actions", []),
            "success_criteria": self._define_success_criteria(task),
            "confidence": best_path.get("score", 0.7),
            "explored_paths": len(candidates)
        }

        logger.info(f"Generated ToT plan exploring {len(candidates)} paths")
        return plan

    def _generate_candidates(self, task: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate candidate reasoning paths."""
        # Simplified: generate multiple approaches
        candidates = []
        for i in range(self.breadth):
            candidates.append({
                "approach": f"approach_{i}",
                "actions": self._generate_actions(task, i),
                "score": 0.5 + (i * 0.1)  # Placeholder scoring
            })
        return candidates

    def _generate_actions(self, task: str, variant: int) -> List[Dict[str, Any]]:
        """Generate action sequence for a specific approach."""
        return [
            {"type": "decompose", "variant": variant},
            {"type": "execute_steps", "parallel": variant % 2 == 0}
        ]

    def _select_best_path(self, candidates: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Select best reasoning path."""
        # Select highest scoring candidate
        return max(candidates, key=lambda c: c.get("score", 0))

    def _infer_io_spec(self, task: str) -> Dict[str, Any]:
        """Infer input/output specification."""
        return {
            "input_type": "generic",
            "output_type": "generic",
            "constraints": []
        }

    def _define_success_criteria(self, task: str) -> Dict[str, Any]:
        """Define success criteria."""
        return {
            "has_result": True,
            "no_errors": True,
            "valid_schema": True
        }


class ReflexionMemory:
    """Reflexion-based episodic memory for self-correction.
    
    Stores feedback about what worked and what failed to improve future attempts.
    """

    def __init__(self):
        self.episodes: List[Dict[str, Any]] = []

    def add(self, task: str, outcome: str, feedback: Dict[str, Any]) -> None:
        """Add reflexion episode."""
        episode = {
            "task": task,
            "outcome": outcome,
            "feedback": feedback,
            "lessons": self._extract_lessons(outcome, feedback)
        }
        self.episodes.append(episode)
        logger.info(f"Added reflexion episode: {outcome}")

    def _extract_lessons(self, outcome: str, feedback: Dict[str, Any]) -> List[str]:
        """Extract lessons from feedback."""
        lessons = []
        if outcome == "failure":
            error_type = feedback.get("error_type", "unknown")
            lessons.append(f"Avoid {error_type} in similar tasks")
        return lessons

    def get_relevant(self, task: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get relevant reflexion episodes."""
        # Simplified: return recent episodes
        return self.episodes[-limit:]

    def should_reflect(self, feedback: List[Dict[str, Any]]) -> bool:
        """Determine if reflection is needed."""
        # Reflect on failures or after multiple retries
        has_failures = any(f.get("category") in ["bad_result", "error"] for f in feedback)
        return has_failures
