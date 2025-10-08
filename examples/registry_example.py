#!/usr/bin/env python3
"""
Example of working with the tool registry directly.
"""

from evomind.registry.tool_registry import ToolRegistry


def main():
    print("EvoMind Tool Registry Example")
    print("=" * 50)
    
    # Create registry
    registry = ToolRegistry()
    
    # List all tools
    print("\n1. Listing all tools:")
    tools = registry.list_all()
    print(f"   Found {len(tools)} tools")
    
    for tool in tools:
        meta = tool["metadata"]
        print(f"\n   - {meta['name']} (v{meta['version']})")
        print(f"     Description: {meta['description']}")
        print(f"     Usage: {meta['usage_count']}")
        print(f"     Success Rate: {meta['success_rate']:.2%}")
    
    # Search for tools
    print("\n2. Searching for 'parse' tools:")
    results = registry.search("parse")
    print(f"   Found {len(results)} matching tools")
    
    for tool in results:
        meta = tool["metadata"]
        print(f"   - {meta['name']}: {meta['description']}")
    
    # Register a new tool
    print("\n3. Registering a new tool:")
    artifact = {
        "code": "def example_tool(data): return data",
        "type": "python_function"
    }
    metadata = {
        "name": "example_tool",
        "description": "An example tool",
        "tags": ["example", "demo"]
    }
    
    tool_id = registry.register(artifact, metadata, "0.1.0")
    print(f"   ✓ Registered: {tool_id}")
    
    # Get specific tool
    print("\n4. Getting tool details:")
    tool = registry.get(tool_id)
    if tool:
        print(f"   ✓ Tool found: {tool['metadata']['name']}")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
