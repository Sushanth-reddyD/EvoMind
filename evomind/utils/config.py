"""Configuration management."""

import os
from typing import Any, Dict, Optional
from pathlib import Path
import yaml
import json
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for EvoMind agent system."""

    # Agent settings
    confidence_threshold: float = 0.7
    max_retries: int = 3

    # LLM settings
    llm_provider: str = "gemini"  # openai, anthropic, gemini
    llm_model: str = "gemini-2.0-flash-exp"
    llm_api_key: Optional[str] = None
    llm_temperature: float = 0.7

    # Sandbox settings
    sandbox_cpu_limit: int = 30
    sandbox_memory_mb: int = 512
    sandbox_timeout: int = 60
    sandbox_network_enabled: bool = False

    # Registry settings
    registry_path: Optional[str] = None

    # Observability settings
    log_level: str = "INFO"
    log_structured: bool = False
    log_file: Optional[str] = None
    metrics_enabled: bool = True

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        return cls(
            confidence_threshold=float(os.getenv("EVOMIND_CONFIDENCE_THRESHOLD", "0.7")),
            max_retries=int(os.getenv("EVOMIND_MAX_RETRIES", "3")),
            llm_provider=os.getenv("EVOMIND_LLM_PROVIDER", "gemini"),
            llm_model=os.getenv("EVOMIND_LLM_MODEL", "gemini-2.0-flash-exp"),
            llm_api_key=os.getenv("EVOMIND_LLM_API_KEY") or os.getenv("GEMINI_API_KEY"),
            sandbox_cpu_limit=int(os.getenv("EVOMIND_SANDBOX_CPU_LIMIT", "30")),
            sandbox_memory_mb=int(os.getenv("EVOMIND_SANDBOX_MEMORY_MB", "512")),
            sandbox_timeout=int(os.getenv("EVOMIND_SANDBOX_TIMEOUT", "60")),
            log_level=os.getenv("EVOMIND_LOG_LEVEL", "INFO"),
            log_structured=os.getenv("EVOMIND_LOG_STRUCTURED", "false").lower() == "true",
            api_host=os.getenv("EVOMIND_API_HOST", "0.0.0.0"),
            api_port=int(os.getenv("EVOMIND_API_PORT", "8000")),
        )

    @classmethod
    def from_file(cls, path: str) -> "Config":
        """Load config from file (YAML or JSON)."""
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        content = file_path.read_text()

        if path.endswith(".yaml") or path.endswith(".yml"):
            data = yaml.safe_load(content)
        elif path.endswith(".json"):
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported config file format: {path}")

        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "confidence_threshold": self.confidence_threshold,
            "max_retries": self.max_retries,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "llm_temperature": self.llm_temperature,
            "sandbox_cpu_limit": self.sandbox_cpu_limit,
            "sandbox_memory_mb": self.sandbox_memory_mb,
            "sandbox_timeout": self.sandbox_timeout,
            "sandbox_network_enabled": self.sandbox_network_enabled,
            "log_level": self.log_level,
            "log_structured": self.log_structured,
            "metrics_enabled": self.metrics_enabled,
            "api_host": self.api_host,
            "api_port": self.api_port,
        }
