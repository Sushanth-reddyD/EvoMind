#!/usr/bin/env python3
"""
Basic example of using EvoMind agent system.

This example demonstrates:
1. Creating an agent
2. Submitting a request
3. Handling the response
"""

from evomind import AgentController


def main():
    print("EvoMind Basic Example")
    print("=" * 50)
    
    # Create agent controller
    print("\n1. Creating agent controller...")
    agent = AgentController()
    print("   ✓ Agent created successfully")
    
    # Submit a simple request
    print("\n2. Submitting request...")
    request = {
        "task": "Transform and analyze data"
    }
    print(f"   Task: {request['task']}")
    
    result = agent.handle_request(request)
    
    # Handle response
    print("\n3. Response received:")
    print(f"   Status: {result['status']}")
    
    if result['status'] == 'success':
        print("   ✓ Task completed successfully!")
        if 'tool_used' in result:
            print(f"   Tool used: {result['tool_used']}")
        if 'metadata' in result:
            retries = result['metadata'].get('retries', 0)
            print(f"   Retries: {retries}")
    elif result['status'] == 'degraded':
        print("   ⚠ Task completed with issues")
        print(f"   Feedback: {result.get('feedback', [])}")
    else:
        print("   ✗ Task failed")
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
