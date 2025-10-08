#!/usr/bin/env python3
"""Command-line interface for EvoMind agent system."""

import argparse
import sys
import json

from evomind.agent.controller import AgentController
from evomind.utils.config import Config
from evomind.observability.logging import setup_logging
from evomind.observability.metrics import get_metrics_collector


def cmd_submit(args):
    """Submit a request to the agent."""
    config = Config.from_env()
    setup_logging(level=config.log_level, structured=config.log_structured)

    agent = AgentController()

    request = {
        "task": args.task
    }

    if args.args:
        request["args"] = json.loads(args.args)

    print(f"Submitting request: {request['task']}")
    result = agent.handle_request(request)

    print(json.dumps(result, indent=2))

    return 0 if result.get("status") == "success" else 1


def cmd_list_tools(args):
    """List available tools."""
    from evomind.registry.tool_registry import ToolRegistry

    registry = ToolRegistry()
    tools = registry.list_all(include_deprecated=args.include_deprecated)

    print(f"Found {len(tools)} tools:")
    for tool in tools:
        meta = tool["metadata"]
        status = " [DEPRECATED]" if meta.get("deprecated") else ""
        print(f"  - {meta['name']} (v{meta['version']}){status}")
        print(f"    {meta['description']}")
        print(f"    Usage: {meta['usage_count']}, Success rate: {meta['success_rate']:.2%}")
        print()

    return 0


def cmd_inspect_tool(args):
    """Inspect a specific tool."""
    from evomind.registry.tool_registry import ToolRegistry

    registry = ToolRegistry()
    tool = registry.get(args.tool_id)

    if not tool:
        print(f"Tool not found: {args.tool_id}", file=sys.stderr)
        return 1

    print(json.dumps(tool["metadata"], indent=2))

    if args.show_code:
        print("\nCode:")
        print("=" * 80)
        print(tool.get("code", "No code available"))

    return 0


def cmd_metrics(args):
    """Show metrics."""
    metrics = get_metrics_collector()
    data = metrics.get_metrics()

    print(json.dumps(data, indent=2))
    return 0


def cmd_dry_run(args):
    """Dry run a tool."""
    from evomind.registry.tool_registry import ToolRegistry
    from evomind.sandbox.executor import SandboxExecutor

    registry = ToolRegistry()
    tool = registry.get(args.tool_id)

    if not tool:
        print(f"Tool not found: {args.tool_id}", file=sys.stderr)
        return 1

    executor = SandboxExecutor()

    tool_args = {}
    if args.args:
        tool_args = json.loads(args.args)

    print(f"Executing tool {args.tool_id}...")
    result = executor.execute(tool, tool_args)

    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "success" else 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="EvoMind - AI Agent System CLI"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Submit command
    submit_parser = subparsers.add_parser("submit", help="Submit a request")
    submit_parser.add_argument("task", help="Task description")
    submit_parser.add_argument("--args", help="Task arguments as JSON")
    submit_parser.set_defaults(func=cmd_submit)

    # List tools command
    list_parser = subparsers.add_parser("list-tools", help="List available tools")
    list_parser.add_argument("--include-deprecated", action="store_true", help="Include deprecated tools")
    list_parser.set_defaults(func=cmd_list_tools)

    # Inspect tool command
    inspect_parser = subparsers.add_parser("inspect", help="Inspect a tool")
    inspect_parser.add_argument("tool_id", help="Tool ID")
    inspect_parser.add_argument("--show-code", action="store_true", help="Show tool code")
    inspect_parser.set_defaults(func=cmd_inspect_tool)

    # Metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Show metrics")
    metrics_parser.set_defaults(func=cmd_metrics)

    # Dry run command
    dryrun_parser = subparsers.add_parser("dry-run", help="Dry run a tool")
    dryrun_parser.add_argument("tool_id", help="Tool ID")
    dryrun_parser.add_argument("--args", help="Tool arguments as JSON")
    dryrun_parser.set_defaults(func=cmd_dry_run)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
