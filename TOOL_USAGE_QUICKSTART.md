# 🚀 Tool Usage Quick Start

## In the UI (Easiest)

### Create a Tool
1. Open UI: `./run_ui.sh` or `streamlit run ui/app.py`
2. Go to "Task Execution" tab
3. Enter task: `"Create a function that filters even numbers"`
4. Click "🚀 Execute Task"
5. ✅ Tool created and executed!

### Reuse a Tool
- **Automatic**: Submit similar task, agent finds existing tool
- **Manual**: Check "History" tab → see all created tools

## In Python Code

```python
from evomind.agent.controller import AgentController

# Initialize
agent = AgentController()

# Create and use tool
result = agent.handle_request({
    "task": "Create a function that calculates sum of numbers"
})

print(result)  # Tool created, executed, result returned
```

## Get Existing Tool

```python
from evomind.registry.tool_registry import ToolRegistry

registry = ToolRegistry()

# Search
tools = registry.search("calculator")

# Get by ID
tool = registry.get("tool_id_here")
```

## Execute Tool Manually

```python
from evomind.sandbox.executor import SandboxExecutor

executor = SandboxExecutor()

# Execute
result = executor.execute(
    tool=tool,
    args={"numbers": [1, 2, 3, 4, 5]}
)

print(result)
```

## Save Tool Code

```python
tool = registry.get("your_tool_id")
code = tool["artifact"]["code"]

# Save to file
with open("my_tool.py", "w") as f:
    f.write(code)
```

## Examples

Run the examples:
```bash
source venv/bin/activate
python examples/reuse_tools.py
python examples/using_tools.py
```

## Full Documentation

See [docs/USING_TOOLS.md](docs/USING_TOOLS.md) for complete guide.
