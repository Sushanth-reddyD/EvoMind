"""Practical Example: Save and Reuse Tools from UI"""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evomind.agent.controller import AgentController
from evomind.registry.tool_registry import ToolRegistry
from evomind.sandbox.executor import SandboxExecutor

def main():
    print("🔧 EvoMind Tool Usage Example")
    print("=" * 60)
    
    # Initialize
    agent = AgentController()
    registry = agent.tool_registry
    executor = agent.sandbox_executor
    
    # Example 1: Create a tool via agent
    print("\n1️⃣  Creating a new tool...")
    print("-" * 60)
    
    task_request = {
        "task": "Create a function that filters even numbers from a list"
    }
    
    result = agent.handle_request(task_request)
    
    if result["status"] == "success":
        tool_id = result.get("tool_used")
        print(f"✅ Tool created: {tool_id}")
        print(f"Result: {result['result']}")
        
        # Example 2: Reuse the tool
        print("\n2️⃣  Reusing the created tool...")
        print("-" * 60)
        
        # Get the tool from registry
        tool = registry.get(tool_id)
        
        if tool:
            # Execute with different data
            test_args = {"input_data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
            reuse_result = executor.execute(tool, test_args)
            print(f"✅ Reuse result: {reuse_result}")
    
    # Example 3: List all available tools
    print("\n3️⃣  Listing all available tools...")
    print("-" * 60)
    
    all_tools = registry.search("", limit=10)
    print(f"Found {len(all_tools)} tools in registry:")
    
    for i, tool in enumerate(all_tools, 1):
        meta = tool["metadata"]
        print(f"  {i}. {meta['name']} (v{meta['version']})")
        print(f"     Description: {meta['description']}")
        print(f"     Usage count: {meta['usage_count']}")
        print()
    
    # Example 4: Search for specific tools
    print("\n4️⃣  Searching for specific tools...")
    print("-" * 60)
    
    search_terms = ["filter", "calculate", "parse"]
    
    for term in search_terms:
        results = registry.search(term)
        print(f"'{term}' → {len(results)} tools found")
    
    # Example 5: Tool statistics
    print("\n5️⃣  Tool usage statistics...")
    print("-" * 60)
    
    if tool_id:
        tool_info = registry.get(tool_id)
        if tool_info:
            meta = tool_info["metadata"]
            print(f"Tool: {meta['name']}")
            print(f"  Version: {meta['version']}")
            print(f"  Success Rate: {meta['success_rate']*100:.1f}%")
            print(f"  Usage Count: {meta['usage_count']}")
            print(f"  Created: {meta['created_at']}")
    
    print("\n" + "=" * 60)
    print("✨ Examples completed!")
    
    # Save tool code to file (optional)
    print("\n📝 Tip: To save a tool's code, use:")
    print("   tool = registry.get('tool_id')")
    print("   code = tool['artifact']['code']")
    print("   Path('my_tool.py').write_text(code)")


if __name__ == "__main__":
    main()
