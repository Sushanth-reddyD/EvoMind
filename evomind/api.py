"""REST API for EvoMind agent system."""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    BaseModel = object

from evomind.agent.controller import AgentController
from evomind.registry.tool_registry import ToolRegistry
from evomind.observability.metrics import get_metrics_collector
from evomind.utils.config import Config

logger = logging.getLogger(__name__)


# Request/Response models
class AgentRequest(BaseModel):
    """Agent request model."""
    task: str
    args: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Agent response model."""
    status: str
    result: Optional[Any] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def create_app(config: Optional[Config] = None) -> Any:
    """Create FastAPI application.
    
    Args:
        config: Configuration object
    
    Returns:
        FastAPI app instance
    """
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI not installed. Install with: pip install fastapi uvicorn")
    
    config = config or Config.from_env()
    
    app = FastAPI(
        title="EvoMind Agent API",
        description="REST API for EvoMind AI Agent System",
        version="0.1.0"
    )
    
    # Initialize components
    agent = AgentController()
    registry = ToolRegistry()
    metrics = get_metrics_collector()
    
    @app.get("/")
    def root():
        """Root endpoint."""
        return {
            "name": "EvoMind Agent API",
            "version": "0.1.0",
            "status": "running"
        }
    
    @app.get("/health")
    def health():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @app.post("/agent/request")
    def submit_request(request: AgentRequest):
        """Submit a request to the agent."""
        start_time = datetime.utcnow()
        
        try:
            result = agent.handle_request({
                "task": request.task,
                "args": request.args or {}
            })
            
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            metrics.record_request(result.get("status", "unknown"), duration_ms)
            
            return JSONResponse(content=result)
        
        except Exception as e:
            logger.error(f"Request failed: {e}", exc_info=True)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            metrics.record_request("error", duration_ms)
            
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/tools")
    def list_tools(include_deprecated: bool = False):
        """List available tools."""
        tools = registry.list_all(include_deprecated=include_deprecated)
        return {
            "count": len(tools),
            "tools": tools
        }
    
    @app.get("/tools/{tool_id}")
    def get_tool(tool_id: str):
        """Get tool details."""
        tool = registry.get(tool_id)
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        return tool
    
    @app.get("/metrics")
    def get_metrics():
        """Get system metrics."""
        return metrics.get_metrics()
    
    @app.get("/config")
    def get_config():
        """Get configuration (sanitized)."""
        config_dict = config.to_dict()
        # Remove sensitive fields
        config_dict.pop("llm_api_key", None)
        return config_dict
    
    return app


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    if not FASTAPI_AVAILABLE:
        print("Error: FastAPI not installed. Install with: pip install fastapi uvicorn")
        return 1
    
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn not installed. Install with: pip install uvicorn")
        return 1
    
    config = Config.from_env()
    app = create_app(config)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    import sys
    run_server()
