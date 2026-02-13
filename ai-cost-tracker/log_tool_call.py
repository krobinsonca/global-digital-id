#!/usr/bin/env python3
"""
Tool call logger for OpenClaw tool wrappers.
Usage: log_tool_call.py --tool <name> --duration <ms> --exit-code <code>
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tracker import get_tracker


def main():
    parser = argparse.ArgumentParser(description="Log tool call to AI Cost Tracker")
    parser.add_argument("--tool", required=True, help="Tool name")
    parser.add_argument("--duration", type=int, required=True, help="Duration in milliseconds")
    parser.add_argument("--exit-code", type=int, default=0, help="Exit code")
    parser.add_argument("--model", help="Model used")
    parser.add_argument("--prompt-tokens", type=int, default=100, help="Estimated prompt tokens")
    parser.add_argument("--completion-tokens", type=int, default=50, help="Estimated completion tokens")
    parser.add_argument("--task-type", default="tool", help="Task type")
    parser.add_argument("--session-id", help="Session ID")
    
    args = parser.parse_args()
    
    tracker = get_tracker()
    
    tracker.log_call(
        model=args.model or "unknown",
        tokens_in=args.prompt_tokens,
        tokens_out=args.completion_tokens,
        task_type=args.task_type,
        session_id=args.session_id or args.tool,
        extra={
            "duration_ms": args.duration,
            "exit_code": args.exit_code,
            "source": "tool_wrapper"
        }
    )
    
    print(f"✅ Logged {args.tool} call: {args.duration}ms")


if __name__ == "__main__":
    main()
