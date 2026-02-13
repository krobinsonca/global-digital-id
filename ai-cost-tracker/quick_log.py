#!/usr/bin/env python3
"""
AI Cost Tracker - Quick logging utility.
Usage: python quick_log.py <model> <tokens_in> <tokens_out> <task_type>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tracker import get_tracker

def main():
    if len(sys.argv) < 5:
        print("Usage: python quick_log.py <model> <tokens_in> <tokens_out> <task_type>")
        print("Example: python quick_log.py gpt-4o 1000 500 coding")
        sys.exit(1)
    
    model = sys.argv[1]
    tokens_in = int(sys.argv[2])
    tokens_out = int(sys.argv[3])
    task_type = sys.argv[4]
    
    tracker = get_tracker()
    call = tracker.log_call(
        model=model,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        task_type=task_type
    )
    
    print(f"✅ Logged: {call.model} - {call.tokens_in} in + {call.tokens_out} out = ${call.cost_estimate:.6f}")

if __name__ == "__main__":
    main()
