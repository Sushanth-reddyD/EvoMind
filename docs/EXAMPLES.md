# Examples

## Basic Usage

### Example 1: Simple Task Execution

```python
from evomind import AgentController

agent = AgentController()

result = agent.handle_request({
    "task": "Parse JSON and extract fields"
})

print(result)
```

### Example 2: Using CLI

```bash
# Submit a task
python -m evomind.cli submit "Transform CSV data to JSON"

# List available tools
python -m evomind.cli list-tools

# Inspect a specific tool
python -m evomind.cli inspect tool_csv_parser_0.1.0 --show-code
```

### Example 3: API Server

```python
from evomind.api import create_app
import uvicorn

app = create_app()
uvicorn.run(app, host="0.0.0.0", port=8000)
```

Then make requests:

```bash
curl -X POST http://localhost:8000/agent/request \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyze dataset and compute statistics",
    "args": {"data": [1, 2, 3, 4, 5]}
  }'
```

## Advanced Examples

### Example 4: Custom Configuration

```python
from evomind import AgentController
from evomind.utils.config import Config

config = Config(
    confidence_threshold=0.8,
    max_retries=5,
    sandbox_memory_mb=1024
)

agent = AgentController(confidence_threshold=config.confidence_threshold)

result = agent.handle_request({
    "task": "Complex data analysis"
})
```

### Example 5: Direct Tool Registry Usage

```python
from evomind.registry.tool_registry import ToolRegistry

registry = ToolRegistry()

# Search for tools
tools = registry.search("json parser")

for tool in tools:
    print(f"Tool: {tool['metadata']['name']}")
    print(f"Version: {tool['metadata']['version']}")
    print(f"Success Rate: {tool['metadata']['success_rate']:.2%}")
```

### Example 6: Custom Sandbox Policies

```python
from evomind.sandbox.executor import SandboxExecutor
from evomind.sandbox.policies import SandboxPolicy, ResourcePolicy, SecurityPolicy

# Define custom policies
policy = SandboxPolicy(
    resource=ResourcePolicy(
        cpu_time_limit=60,
        memory_limit_mb=1024,
        wall_time_limit=120
    ),
    security=SecurityPolicy(
        network_enabled=False,
        filesystem_readonly=True
    )
)

executor = SandboxExecutor(default_policy=policy)

# Execute with custom policy
result = executor.execute(tool, args, policy=policy)
```

### Example 7: Metrics and Monitoring

```python
from evomind.observability.metrics import get_metrics_collector

metrics = get_metrics_collector()

# Record custom metrics
metrics.increment_counter("custom_operations")
metrics.record_histogram("operation_duration_ms", 123.45)

# Get metrics snapshot
data = metrics.get_metrics()
print(data)
```

### Example 8: Error Handling

```python
from evomind import AgentController

agent = AgentController()

try:
    result = agent.handle_request({
        "task": "Complex operation that might fail"
    })
    
    if result["status"] == "success":
        print("Success:", result["result"])
    elif result["status"] == "degraded":
        print("Partial success:", result.get("partial_result"))
        print("Issues:", result.get("feedback"))
    else:
        print("Failed:", result.get("message"))
        
except Exception as e:
    print(f"Error: {e}")
```

## Testing Examples

### Example 9: Unit Testing

```python
import pytest
from evomind.agent.controller import AgentController

def test_simple_request():
    agent = AgentController()
    
    result = agent.handle_request({
        "task": "test task"
    })
    
    assert result is not None
    assert "status" in result

def test_state_transitions():
    from evomind.agent.state import AgentState, StateType
    
    state = AgentState()
    state.transition(StateType.PLAN)
    
    assert state.current_state == StateType.PLAN
    assert len(state.history) == 1
```

### Example 10: Integration Testing

```python
def test_end_to_end_flow():
    from evomind import AgentController
    from evomind.registry.tool_registry import ToolRegistry
    
    # Setup
    agent = AgentController()
    registry = ToolRegistry()
    
    # Execute task
    result = agent.handle_request({
        "task": "Parse JSON data"
    })
    
    # Verify
    assert result["status"] in ["success", "degraded"]
    
    # Check tool was registered
    tools = registry.list_all()
    assert len(tools) > 0
```

## Production Examples

### Example 11: Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY evomind/ ./evomind/

ENV EVOMIND_LOG_LEVEL=INFO
ENV EVOMIND_SANDBOX_MEMORY_MB=512

CMD ["python", "-m", "evomind.api"]
```

### Example 12: Kubernetes Configuration

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: evomind-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: evomind
  template:
    metadata:
      labels:
        app: evomind
    spec:
      containers:
      - name: evomind
        image: evomind:latest
        ports:
        - containerPort: 8000
        env:
        - name: EVOMIND_LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

### Example 13: Configuration Management

```yaml
# config.yaml
confidence_threshold: 0.75
max_retries: 3

llm_provider: openai
llm_model: gpt-4

sandbox_cpu_limit: 30
sandbox_memory_mb: 512
sandbox_timeout: 60

log_level: INFO
log_structured: true

api_host: 0.0.0.0
api_port: 8000
```

```python
from evomind.utils.config import Config

config = Config.from_file("config.yaml")
agent = AgentController(confidence_threshold=config.confidence_threshold)
```

## Common Patterns

### Pattern 1: Retry with Exponential Backoff

```python
from evomind.utils.retry import with_retry, RetryPolicy

@with_retry(policy=RetryPolicy(max_attempts=5, initial_delay=1.0))
def flaky_operation():
    # Operation that might fail
    pass
```

### Pattern 2: Circuit Breaker

```python
from evomind.utils.retry import CircuitBreaker

breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)

def call_external_service():
    return breaker.call(external_api_call, args)
```

### Pattern 3: Structured Logging

```python
from evomind.observability.logging import setup_logging

setup_logging(
    level="INFO",
    structured=True,
    log_file="evomind.log"
)
```

These examples demonstrate the flexibility and power of the EvoMind system for various use cases.
