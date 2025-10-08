"""Example: How to use created tools in EvoMind"""

from evomind.agent.controller import AgentController
from evomind.registry.tool_registry import ToolRegistry
from evomind.sandbox.executor import SandboxExecutor

# Initialize components
agent = AgentController()
registry = ToolRegistry()
executor = SandboxExecutor()

# Method 1: Create and Execute a Tool Directly
# ==============================================
print("Method 1: Create and Execute Tool")
print("-" * 50)

# Submit a task
request = {
    "task": "Create a function that calculates fibonacci numbers up to n"
}

# Agent handles everything: plan, create, execute
result = agent.handle_request(request)

if result["status"] == "success":
    print("✅ Task completed!")
    print(f"Tool used: {result['tool_used']}")
    print(f"Result: {result['result']}")
else:
    print(f"❌ Task failed: {result.get('message')}")

print("\n")

# Method 2: Search and Reuse Existing Tools
# ==========================================
print("Method 2: Search and Reuse Tools")
print("-" * 50)

# Search for existing tools
tools = registry.search("fibonacci")

if tools:
    tool = tools[0]  # Get first match
    print(f"Found tool: {tool['metadata']['name']}")
    
    # Execute the tool with arguments
    args = {"n": 10}
    result = executor.execute(tool, args)
    
    print(f"Execution result: {result}")
else:
    print("No tools found")

print("\n")

# Method 3: Get Tool by ID and Execute
# ====================================
print("Method 3: Get Tool by ID")
print("-" * 50)

# If you know the tool ID (from previous creation)
tool_id = "fibonacci_generator_v0.1.0"  # Example ID

tool = registry.get(tool_id)

if tool:
    print(f"Retrieved tool: {tool['metadata']['name']}")
    
    # Execute with custom arguments
    args = {"n": 5}
    result = executor.execute(tool, args)
    
    print(f"Result: {result}")
else:
    print(f"Tool {tool_id} not found")

print("\n")

# Method 4: Direct Code Execution (No Registry)
# ==============================================
print("Method 4: Direct Code Execution")
print("-" * 50)

# If you have the code directly
tool_code = '''
def calculate_sum(input_data: dict) -> dict:
    """Calculate sum of numbers."""
    numbers = input_data.get("numbers", [])
    total = sum(numbers)
    return {
        "status": "success",
        "result": {"sum": total}
    }
'''

# Create tool artifact
tool = {
    "tool_id": "temp_sum_calculator",
    "code": tool_code
}

# Execute
args = {"numbers": [1, 2, 3, 4, 5]}
result = executor.execute(tool, args)

print(f"Direct execution result: {result}")

print("\n")

# Method 5: Using the Code Generator Directly
# ===========================================
print("Method 5: Using Code Generator")
print("-" * 50)

from evomind.codegen.generator import CodeGenerator

generator = CodeGenerator(use_llm=False)  # Use templates for this example

# Generate a tool
spec = {
    "name": "my_custom_tool",
    "description": "A custom tool that processes data",
    "io_spec": {
        "input": "dict with 'data' key",
        "output": "dict with 'processed' key"
    },
    "constraints": {
        "timeout": 30,
        "memory_mb": 512
    },
    "tests": []
}

tool_result = generator.create_tool(spec)

if tool_result["status"] == "READY":
    print("✅ Tool generated successfully!")
    print(f"Tool ID: {tool_result['tool_id']}")
    print(f"\nGenerated Code:\n{tool_result['code']}")
    
    # Now you can register and use it
    tool_id = registry.register(
        artifact=tool_result["artifact"],
        metadata={"name": spec["name"], "description": spec["description"]},
        version=tool_result["version"]
    )
    print(f"\n✅ Tool registered with ID: {tool_id}")
else:
    print(f"❌ Generation failed: {tool_result}")

print("\n" + "="*50)
print("All methods demonstrated!")
