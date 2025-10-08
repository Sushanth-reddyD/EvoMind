# Using Created Tools in EvoMind

This guide explains how to use tools you've created in EvoMind.

## 🎯 Quick Reference

### Via UI (Streamlit)

1. **Create a tool** in the "Task Execution" or "Code Generator" tab
2. **View in History** tab to see all created tools
3. **Reuse tools** by submitting similar tasks (agent will find existing tools)

### Via Python API

```python
from evomind.agent.controller import AgentController

agent = AgentController()

# Create and use a tool
result = agent.handle_request({"task": "Your task here"})
```

## 📚 Detailed Methods

### Method 1: Automatic Reuse (Recommended)

When you submit a task, the agent automatically searches for existing tools:

```python
# First time: Creates new tool
agent.handle_request({"task": "Calculate fibonacci numbers"})

# Second time: Finds and reuses the existing tool
agent.handle_request({"task": "Calculate fibonacci sequence"})
```

### Method 2: Direct Tool Retrieval

```python
from evomind.registry.tool_registry import ToolRegistry

registry = ToolRegistry()

# Search by name/description
tools = registry.search("fibonacci")

# Get by exact ID
tool = registry.get("fibonacci_generator_v0.1.0")
```

### Method 3: Manual Execution

```python
from evomind.sandbox.executor import SandboxExecutor

executor = SandboxExecutor()

# Get tool from registry
tool = registry.get("your_tool_id")

# Execute with arguments
args = {"input_data": [1, 2, 3, 4, 5]}
result = executor.execute(tool, args)

print(result)
```

### Method 4: Export and Save Tools

```python
from pathlib import Path

# Get tool
tool = registry.get("your_tool_id")

# Extract code
code = tool["artifact"]["code"]

# Save to file
Path("my_tool.py").write_text(code)

# Now you can import and use it anywhere
```

## 🖥️ Using Tools in the UI

### Task Execution Tab

1. Enter your task description
2. Click "🚀 Execute Task"
3. Tool is created and executed automatically
4. Result displayed with tool ID

### History Tab

1. View all previously created tools
2. Click on any task to see:
   - Task description
   - Tool used
   - Generated code
   - Execution results
   - Status and metadata

### Code Generator Tab

1. Specify function details
2. Click "🔨 Generate Code"
3. View generated code
4. Download or copy the code
5. Tool is registered for future use

## 🔄 Tool Lifecycle

```
1. Create Tool
   ↓
2. Validate & Test
   ↓
3. Register in Registry
   ↓
4. Execute with Arguments
   ↓
5. Update Statistics (usage count, success rate)
   ↓
6. Reuse or Deprecate
```

## 📊 Tool Information

Each tool has metadata:

```python
tool_info = registry.get("tool_id")

metadata = tool_info["metadata"]
# {
#   "id": "unique_id",
#   "name": "tool_name",
#   "version": "0.1.0",
#   "description": "What the tool does",
#   "usage_count": 5,
#   "success_rate": 0.95,
#   "created_at": "2025-10-08T...",
#   "deprecated": false
# }
```

## 🎓 Best Practices

### 1. Descriptive Task Names

Good:
```
"Create a function that validates email addresses"
```

Bad:
```
"Make email thing"
```

### 2. Reuse When Possible

Search before creating:
```python
# Check if tool exists
existing = registry.search("email validator")

if existing:
    # Reuse existing tool
    tool = existing[0]
else:
    # Create new tool
    agent.handle_request({"task": "..."})
```

### 3. Update Tool Statistics

After each use:
```python
registry.update_stats(tool_id, success=True)
```

### 4. Export Important Tools

Save production-ready tools:
```python
tool = registry.get("production_tool_id")
code = tool["artifact"]["code"]
Path("production/tools/my_tool.py").write_text(code)
```

## 🔍 Finding Tools

### By Name/Description
```python
tools = registry.search("calculator")
```

### By IO Specification
```python
tools = registry.search(
    query="data processor",
    io_spec={"input_type": "list", "output_type": "dict"}
)
```

### All Tools
```python
all_tools = registry.search("", limit=100)
```

## 💡 Examples

See the examples directory:

1. `examples/using_tools.py` - All usage methods
2. `examples/reuse_tools.py` - Practical reuse example
3. `examples/basic_usage.py` - Basic agent usage
4. `examples/advanced_usage.py` - Advanced patterns

## 🚀 Running Examples

```bash
# Activate virtual environment
source venv/bin/activate

# Run example
python examples/reuse_tools.py
```

## ❓ Troubleshooting

### Tool Not Found

```python
tool = registry.get("tool_id")
if not tool:
    # Tool may have been deprecated or not created
    # Check with search:
    results = registry.search("tool name")
```

### Execution Failed

```python
result = executor.execute(tool, args)

if result["status"] == "error":
    print(f"Error: {result['error']}")
    print(f"Traceback: {result.get('traceback')}")
```

### Tool Deprecated

```python
# Check if tool is deprecated
if tool["metadata"]["deprecated"]:
    # Find alternative or create new version
    alternatives = registry.search(tool["metadata"]["name"])
```

## 📖 Related Documentation

- [ARCHITECTURE.md](../docs/ARCHITECTURE.md) - System architecture
- [EXAMPLES.md](../docs/EXAMPLES.md) - Usage examples
- [README.md](../README.md) - Getting started

## 🤝 Contributing

Found a better way to use tools? Update this guide!
