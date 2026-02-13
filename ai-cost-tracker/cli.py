#!/usr/bin/env python3
"""
AI Cost Tracker - CLI Reporter.
Provides reporting capabilities with --days, --model, --task filters.
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from tracker import CostTracker, PricingEngine


def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:.6f}" if amount < 0.01 else f"${amount:.4f}"


def format_number(n: int) -> str:
    """Format number with commas."""
    return f"{n:,}"


def cmd_stats(args):
    """Show overall statistics."""
    tracker = CostTracker(data_dir=args.data_dir)
    stats = tracker.get_stats(days=args.days, model=args.model, task_type=args.task)
    
    print("\n" + "=" * 60)
    print("AI COST TRACKING - STATISTICS")
    print("=" * 60)
    
    if args.days:
        print(f"Period: Last {args.days} days")
    if args.model:
        print(f"Model: {args.model}")
    if args.task:
        print(f"Task: {args.task}")
    
    print("-" * 60)
    print(f"Total API Calls:  {format_number(stats['total_calls'])}")
    print(f"Total Tokens In:  {format_number(stats['total_tokens_in'])}")
    print(f"Total Tokens Out: {format_number(stats['total_tokens_out'])}")
    print(f"Total Cost:       {format_currency(stats['total_cost'])}")
    print("=" * 60 + "\n")


def cmd_models(args):
    """List available models with pricing."""
    pricing = PricingEngine()
    models = pricing.list_all_models()
    
    print("\n" + "=" * 60)
    print("AVAILABLE MODELS & PRICING")
    print("=" * 60)
    
    current_provider = None
    for model in sorted(models, key=lambda x: (x['provider'], x['model'])):
        if model['provider'] != current_provider:
            current_provider = model['provider']
            print(f"\n📦 {current_provider.upper()}")
            print("-" * 40)
        
        price_info = f"${model['input_per_million']:.2f}/M in → ${model['output_per_million']:.2f}/M out"
        print(f"  {model['model']}")
        print(f"    └─ {model['description']}")
        print(f"    └─ {price_info}")
    
    print()


def cmd_recent(args):
    """Show recent LLM calls."""
    tracker = CostTracker(data_dir=args.data_dir)
    calls = tracker.get_recent_calls(limit=args.limit, days=args.days)
    
    print("\n" + "=" * 80)
    print("RECENT LLM CALLS")
    print("=" * 80)
    print(f"{'Timestamp':<25} {'Model':<35} {'Task':<15} {'Tokens':<10} {'Cost':<10}")
    print("-" * 80)
    
    for call in calls:
        ts = call.timestamp[:19].replace('T', ' ')
        model = call.model[:33] + '..' if len(call.model) > 35 else call.model
        task = call.task_type[:13] + '..' if len(call.task_type) > 15 else call.task_type
        tokens = f"{call.tokens_in}+{call.tokens_out}"
        cost = format_currency(call.cost_estimate)
        
        print(f"{ts:<25} {model:<35} {task:<15} {tokens:<10} {cost:<10}")
    
    print("=" * 80 + "\n")


def cmd_daily(args):
    """Show daily cost breakdown."""
    tracker = CostTracker(data_dir=args.data_dir)
    daily = tracker.get_daily_costs(days=args.days)
    
    print("\n" + "=" * 70)
    print("DAILY COST BREAKDOWN")
    print("=" * 70)
    print(f"{'Date':<12} {'Calls':<8} {'Tokens In':<12} {'Tokens Out':<12} {'Cost':<12}")
    print("-" * 70)
    
    total_calls = total_tokens_in = total_tokens_out = total_cost = 0
    
    for day in daily:
        print(f"{day['date']:<12} {day['calls']:<8} {day['tokens_in']:<12} "
              f"{day['tokens_out']:<12} {format_currency(day['cost']):<12}")
        total_calls += day['calls']
        total_tokens_in += day['tokens_in']
        total_tokens_out += day['tokens_out']
        total_cost += day['cost']
    
    print("-" * 70)
    print(f"{'TOTAL':<12} {total_calls:<8} {total_tokens_in:<12} {total_tokens_out:<12} "
          f"{format_currency(total_cost):<12}")
    print("=" * 70 + "\n")


def cmd_by_model(args):
    """Show cost breakdown by model."""
    tracker = CostTracker(data_dir=args.data_dir)
    breakdown = tracker.get_model_breakdown(days=args.days)
    
    print("\n" + "=" * 80)
    print("COST BREAKDOWN BY MODEL")
    print("=" * 80)
    print(f"{'Model':<35} {'Provider':<12} {'Calls':<8} {'Cost':<12}")
    print("-" * 80)
    
    total_cost = 0
    for item in breakdown:
        model = item['model'][:33] + '..' if len(item['model']) > 35 else item['model']
        print(f"{model:<35} {item['provider']:<12} {item['calls']:<8} "
              f"{format_currency(item['cost']):<12}")
        total_cost += item['cost']
    
    print("-" * 80)
    print(f"{'TOTAL COST:':<55} {format_currency(total_cost)}")
    print("=" * 80 + "\n")


def cmd_by_task(args):
    """Show cost breakdown by task type."""
    tracker = CostTracker(data_dir=args.data_dir)
    breakdown = tracker.get_task_breakdown(days=args.days)
    
    print("\n" + "=" * 80)
    print("COST BREAKDOWN BY TASK TYPE")
    print("=" * 80)
    print(f"{'Task Type':<30} {'Calls':<8} {'Cost':<15}")
    print("-" * 80)
    
    total_cost = 0
    for item in breakdown:
        task = item['task_type'][:28] + '..' if len(item['task_type']) > 30 else item['task_type']
        print(f"{task:<30} {item['calls']:<8} {format_currency(item['cost']):<15}")
        total_cost += item['cost']
    
    print("-" * 80)
    print(f"{'TOTAL COST:':<45} {format_currency(total_cost)}")
    print("=" * 80 + "\n")


def cmd_export(args):
    """Export data to JSONL."""
    tracker = CostTracker(data_dir=args.data_dir)
    
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_file = f"ai_costs_export_{timestamp}.jsonl"
    
    count = tracker.export_to_jsonl(output_file)
    print(f"\n✅ Exported {count} records to {output_file}\n")


def cmd_import(args):
    """Import data from JSONL."""
    tracker = CostTracker(data_dir=args.data_dir)
    
    if not Path(args.input).exists():
        print(f"\n❌ File not found: {args.input}\n")
        return 1
    
    count = tracker.import_from_jsonl(args.input)
    print(f"\n✅ Imported {count} records from {args.input}\n")


def cmd_estimate(args):
    """Estimate cost for a hypothetical call."""
    pricing = PricingEngine()
    
    if args.model:
        cost = pricing.calculate_cost(args.model, args.prompt_tokens, args.completion_tokens)
        pricing_info = pricing.get_pricing(args.model)
        
        print(f"\n💰 Cost Estimate for {args.model}")
        print("=" * 50)
        print(f"Input tokens:  {format_number(args.prompt_tokens)}")
        print(f"Output tokens: {format_number(args.completion_tokens)}")
        print(f"Total tokens:  {format_number(args.prompt_tokens + args.completion_tokens)}")
        print(f"Estimated cost: {format_currency(cost)}")
        
        if pricing_info:
            print(f"Provider: {pricing_info.get('provider', 'unknown')}")
            print(f"Rate: ${pricing_info['input_cost_per_million']}/M in → "
                  f"${pricing_info['output_cost_per_million']}/M out")
        print()
    else:
        # Show estimate for all matching models
        models = pricing.list_all_models()
        print(f"\n💰 Cost Estimates for {args.prompt_tokens} in + {args.completion_tokens} out tokens")
        print("=" * 70)
        print(f"{'Model':<40} {'Provider':<12} {'Cost':<12}")
        print("-" * 70)
        
        for model in sorted(models, key=lambda x: pricing.calculate_cost(x['model'], args.prompt_tokens, args.completion_tokens)):
            cost = pricing.calculate_cost(model['model'], args.prompt_tokens, args.completion_tokens)
            print(f"{model['model']:<40} {model['provider']:<12} {format_currency(cost):<12}")
        print()


def cmd_cleanup(args):
    """Clean up old records."""
    tracker = CostTracker(data_dir=args.data_dir)
    
    count = tracker.cleanup_old_records(days=args.days)
    print(f"\n🧹 Removed {count} records older than {args.days} days\n")
    
    if args.vacuum:
        tracker.vacuum()
        print("✅ Database vacuumed\n")


def cmd_serve(args):
    """Start the SQLite database for external queries."""
    import sqlite3
    from threading import Thread
    
    db_path = CostTracker(data_dir=args.data_dir).db_file
    
    print(f"\n🗄️  SQLite database ready at: {db_path}")
    print("   Use: sqlite3 ai_costs.db")
    print("   Example queries:")
    print("     SELECT COUNT(*), SUM(cost_estimate) FROM llm_calls;")
    print("     SELECT model, SUM(cost_estimate) FROM llm_calls GROUP BY model;")
    print("     SELECT task_type, SUM(cost_estimate) FROM llm_calls GROUP BY task_type;")
    print("\n💡 Press Ctrl+C to exit\n")
    
    # Keep running with a simple wait
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Database server stopped\n")


def main():
    parser = argparse.ArgumentParser(
        description="AI Cost Tracker - Track and report LLM API usage and costs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ai-cost stats                         # Show overall statistics
  ai-cost stats --days 7                # Last 7 days
  ai-cost stats --model gpt-4o          # Specific model
  ai-cost models                        # List all models with pricing
  ai-cost recent                        # Show recent calls
  ai-cost daily                         # Daily breakdown
  ai-cost by-model                      # Breakdown by model
  ai-cost by-task                       # Breakdown by task type
  ai-cost estimate --model gpt-4o --prompt-tokens 1000 --completion-tokens 500
  ai-cost export --output backup.jsonl  # Export to JSONL
  ai-cost import --input backup.jsonl   # Import from JSONL
        """
    )
    
    parser.add_argument(
        "--data-dir",
        default="~/.ai-cost-tracker",
        help="Data directory (default: ~/.ai-cost-tracker)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show overall statistics")
    stats_parser.add_argument("--days", type=int, help="Filter by days")
    stats_parser.add_argument("--model", help="Filter by model")
    stats_parser.add_argument("--task", help="Filter by task type")
    
    # Models command
    subparsers.add_parser("models", help="List available models with pricing")
    
    # Recent command
    recent_parser = subparsers.add_parser("recent", help="Show recent LLM calls")
    recent_parser.add_argument("--limit", type=int, default=50, help="Number of records")
    recent_parser.add_argument("--days", type=int, help="Filter by days")
    
    # Daily command
    daily_parser = subparsers.add_parser("daily", help="Show daily cost breakdown")
    daily_parser.add_argument("--days", type=int, default=30, help="Number of days")
    
    # By-model command
    by_model_parser = subparsers.add_parser("by-model", help="Show cost by model")
    by_model_parser.add_argument("--days", type=int, help="Filter by days")
    
    # By-task command
    by_task_parser = subparsers.add_parser("by-task", help="Show cost by task type")
    by_task_parser.add_argument("--days", type=int, help="Filter by days")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export to JSONL")
    export_parser.add_argument("--output", help="Output file path")
    
    # Import command
    import_parser = subparsers.add_parser("import", help="Import from JSONL")
    import_parser.add_argument("--input", required=True, help="Input file path")
    
    # Estimate command
    estimate_parser = subparsers.add_parser("estimate", help="Estimate cost for a call")
    estimate_parser.add_argument("--model", help="Model to estimate for")
    estimate_parser.add_argument("--prompt-tokens", type=int, default=1000, help="Input tokens")
    estimate_parser.add_argument("--completion-tokens", type=int, default=500, help="Output tokens")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up old records")
    cleanup_parser.add_argument("--days", type=int, default=90, help="Keep records from last N days")
    cleanup_parser.add_argument("--vacuum", action="store_true", help="Vacuum database after cleanup")
    
    # Serve command
    subparsers.add_parser("serve", help="Show database location for external queries")
    
    args = parser.parse_args()
    
    # Expand data directory path
    args.data_dir = str(Path(args.data_dir).expanduser())
    
    # Route to appropriate command
    commands = {
        "stats": cmd_stats,
        "models": cmd_models,
        "recent": cmd_recent,
        "daily": cmd_daily,
        "by-model": cmd_by_model,
        "by-task": cmd_by_task,
        "export": cmd_export,
        "import": cmd_import,
        "estimate": cmd_estimate,
        "cleanup": cmd_cleanup,
        "serve": cmd_serve
    }
    
    if args.command is None:
        parser.print_help()
        return 1
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
