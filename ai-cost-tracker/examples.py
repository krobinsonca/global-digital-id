#!/usr/bin/env python3
"""
AI Cost Tracker - Usage Examples and Quick Reference.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from tracker import CostTracker, PricingEngine


def example_basic_tracking():
    """Basic tracking example."""
    tracker = CostTracker()
    
    # Log a single call
    call = tracker.log_call(
        model="gpt-4o",
        tokens_in=1500,
        tokens_out=500,
        task_type="coding"
    )
    
    print(f"Logged call: {call.model} - ${call.cost_estimate:.6f}")


def example_pricing_lookup():
    """Look up pricing for a model."""
    pricing = PricingEngine()
    
    models = pricing.list_all_models()
    print(f"Total models tracked: {len(models)}")
    
    # Get specific model pricing
    model_pricing = pricing.get_pricing("gpt-4o")
    if model_pricing:
        print(f"GPT-4o: ${model_pricing['input_cost_per_million']}/M in → ${model_pricing['output_cost_per_million']}/M out")


def example_cost_calculation():
    """Calculate cost for a hypothetical call."""
    pricing = PricingEngine()
    
    cost = pricing.calculate_cost(
        model="claude-3-5-sonnet-20241022",
        tokens_in=10000,
        tokens_out=5000
    )
    
    print(f"Cost for 10K in + 5K out on Claude 3.5 Sonnet: ${cost:.4f}")


def example_getting_stats():
    """Get statistics."""
    tracker = CostTracker()
    
    # Overall stats
    stats = tracker.get_stats()
    print(f"Total cost: ${stats['total_cost']:.4f}")
    
    # Last 7 days
    weekly = tracker.get_stats(days=7)
    print(f"Weekly cost: ${weekly['total_cost']:.4f}")
    
    # By model
    by_model = tracker.get_model_breakdown(days=7)
    for model in by_model[:5]:
        print(f"  {model['model']}: ${model['cost']:.4f}")


def example_daily_breakdown():
    """Get daily breakdown."""
    tracker = CostTracker()
    
    daily = tracker.get_daily_costs(days=30)
    for day in daily[:7]:
        print(f"{day['date']}: ${day['cost']:.4f} ({day['calls']} calls)")


def example_export_import():
    """Export and import data."""
    tracker = CostTracker()
    
    # Export
    count = tracker.export_to_jsonl("/tmp/ai-costs-backup.jsonl")
    print(f"Exported {count} records")
    
    # Import
    count = tracker.import_from_jsonl("/tmp/ai-costs-backup.jsonl")
    print(f"Imported {count} records")


def example_openclaw_integration():
    """OpenClaw integration example."""
    from openclaw_integration import OpenClawIntegrator
    
    integrator = OpenClawIntegrator()
    
    # Get default model
    model = integrator.get_default_model()
    print(f"Default model: {model}")
    
    # Generate report
    report = integrator.generate_openclaw_report(days=7)
    print(f"Weekly calls: {report['summary']['total_calls']}")
    print(f"Weekly cost: ${report['summary']['total_cost']:.4f}")


def example_programmatic_usage():
    """Full programmatic example."""
    from tracker import CostTracker, PricingEngine
    
    # Initialize
    tracker = CostTracker()
    pricing = PricingEngine()
    
    # Log several calls
    calls = [
        ("gpt-4o", 2000, 800, "coding"),
        ("claude-3-5-sonnet-20241022", 1500, 600, "writing"),
        ("gemini-1.5-flash", 3000, 1000, "analysis"),
    ]
    
    for model, tin, tout, task in calls:
        # Calculate expected cost
        expected_cost = pricing.calculate_cost(model, tin, tout)
        
        # Log call
        call = tracker.log_call(
            model=model,
            tokens_in=tin,
            tokens_out=tout,
            task_type=task
        )
        
        print(f"📊 {model} ({task}): {tin}+{tout} tokens = ${call.cost_estimate:.4f} (expected: ${expected_cost:.4f})")
    
    # Get summary
    stats = tracker.get_stats()
    print(f"\n📈 Total: {stats['total_calls']} calls, ${stats['total_cost']:.4f}")


if __name__ == "__main__":
    print("=" * 60)
    print("AI Cost Tracker - Usage Examples")
    print("=" * 60)
    
    print("\n1. Basic Tracking")
    example_basic_tracking()
    
    print("\n2. Pricing Lookup")
    example_pricing_lookup()
    
    print("\n3. Cost Calculation")
    example_cost_calculation()
    
    print("\n4. Statistics")
    example_getting_stats()
    
    print("\n5. Daily Breakdown")
    example_daily_breakdown()
    
    print("\n6. Export/Import")
    example_export_import()
    
    print("\n7. OpenClaw Integration")
    example_openclaw_integration()
    
    print("\n8. Programmatic Usage")
    example_programmatic_usage()
    
    print("\n" + "=" * 60)
    print("Run 'python cli.py --help' for CLI usage")
    print("=" * 60)
