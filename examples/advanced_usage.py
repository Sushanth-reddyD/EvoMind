#!/usr/bin/env python3
"""
Advanced example showing custom configuration and error handling.
"""

from evomind import AgentController
from evomind.utils.config import Config
from evomind.observability.logging import setup_logging


def main():
    print("EvoMind Advanced Example")
    print("=" * 50)
    
    # Setup logging
    setup_logging(level="INFO", structured=False)
    
    # Create custom configuration
    config = Config(
        confidence_threshold=0.8,
        max_retries=5,
        sandbox_memory_mb=1024
    )
    
    # Create agent with custom config
    agent = AgentController(
        confidence_threshold=config.confidence_threshold
    )
    
    # Multiple requests
    tasks = [
        "Parse JSON data",
        "Transform CSV to JSON",
        "Calculate statistics"
    ]
    
    for i, task in enumerate(tasks, 1):
        print(f"\n{i}. Processing: {task}")
        
        try:
            result = agent.handle_request({"task": task})
            
            if result["status"] == "success":
                print("   ✓ Success")
            else:
                print(f"   ⚠ Status: {result['status']}")
        
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
