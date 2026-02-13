"""
AI Cost Tracker - OpenClaw Integration.
Integrates with OpenClaw crons and tools for automatic tracking.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from tracker import CostTracker, PricingEngine


# OpenClaw tool integration

@dataclass
class OpenClawTool:
    """Represents an OpenClaw tool that makes LLM calls."""
    name: str
    path: str
    is_llm_tool: bool = True


class OpenClawIntegrator:
    """Integrates AI Cost Tracker with OpenClaw."""
    
    def __init__(self, workspace_path: Optional[str] = None):
        if workspace_path is None:
            workspace_path = "/home/legion/.openclaw/workspace"
        self.workspace = Path(workspace_path)
        self.tracker = CostTracker()
        self.pricing = PricingEngine()
    
    def discover_tools(self) -> List[OpenClawTool]:
        """Discover OpenClaw tools that make LLM calls."""
        tools = []
        
        # Look for tools in common locations
        tool_paths = [
            self.workspace / "hamono" / "tools",
            self.workspace / "apexform" / "tools",
            self.workspace,
        ]
        
        for tool_path in tool_paths:
            if not tool_path.exists():
                continue
            
            for item in tool_path.rglob("*"):
                if item.is_file() and item.suffix in {".py", ".js", ".ts"}:
                    # Check if file likely makes LLM calls
                    content = item.read_text(errors="ignore") if item.stat().st_size < 100000 else ""
                    llm_indicators = [
                        "openai", "anthropic", "google.generativeai", "langchain",
                        "openrouter", "claude", "gpt-", "gemini", "model_name"
                    ]
                    is_llm = any(indicator in content.lower() for indicator in llm_indicators)
                    
                    tools.append(OpenClawTool(
                        name=item.stem,
                        path=str(item),
                        is_llm_tool=is_llm
                    ))
        
        return tools
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration from OpenClaw environment."""
        config = {}
        
        # Check for common environment variables
        env_vars = [
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY",
            "XAI_API_KEY", "OPENROUTER_API_KEY",
            "DEFAULT_MODEL", "LLM_MODEL", "ANTHROPIC_MODEL",
            "OPENAI_MODEL", "GOOGLE_MODEL"
        ]
        
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                config[var.lower()] = value
        
        return config
    
    def get_default_model(self) -> str:
        """Get the default model from OpenClaw configuration."""
        # Check environment
        for key in ["default_model", "llm_model", "anthropic_model", "openai_model", "google_model"]:
            model = os.environ.get(key.upper())
            if model:
                return model
        
        # Check common config files
        config_files = [
            self.workspace / "CLAUDE.md",
            self.workspace / ".claude" / "settings.json",
            self.workspace / "hamono" / ".env",
            self.workspace / "apexform" / ".env",
        ]
        
        for config_file in config_files:
            if config_file.exists():
                content = config_file.read_text()
                if "model" in content.lower():
                    # Try to extract model name
                    for line in content.split('\n'):
                        if "model" in line.lower() and "=" in line:
                            try:
                                _, model = line.split("=", 1)
                                return model.strip().strip('"\'')
                            except:
                                pass
        
        return "unknown"
    
    def log_openclaw_session(
        self,
        session_id: str,
        task_type: str,
        calls: List[Dict[str, Any]]
    ) -> int:
        """Log a complete OpenClaw session."""
        count = 0
        model = self.get_default_model()
        
        for call in calls:
            self.tracker.log_call(
                model=call.get("model", model),
                tokens_in=call.get("tokens_in", 0),
                tokens_out=call.get("tokens_out", 0),
                task_type=task_type,
                session_id=session_id,
                request_id=call.get("request_id"),
                extra={
                    "source": "openclaw",
                    "duration_ms": call.get("duration_ms"),
                    "status": call.get("status")
                }
            )
            count += 1
        
        return count
    
    def generate_openclaw_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate a report suitable for OpenClaw consumption."""
        stats = self.tracker.get_stats(days=days)
        daily = self.tracker.get_daily_costs(days=days)
        models = self.tracker.get_model_breakdown(days=days)
        tasks = self.tracker.get_task_breakdown(days=days)
        
        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "period_days": days,
            "summary": stats,
            "daily_breakdown": daily[:14],  # Last 14 days max
            "model_breakdown": models[:10],  # Top 10 models
            "task_breakdown": tasks[:10],  # Top 10 tasks
            "providers": self.pricing.list_providers(),
            "total_models_tracked": len(models)
        }
    
    def create_cron_template(self) -> str:
        """Create a cron template for OpenClaw integration."""
        return '''# AI Cost Tracker - OpenClaw Cron Jobs
# Add these to your crontab (crontab -e)

# Daily cost summary at 6 PM
0 18 * * * /usr/bin/python3 {data_dir}/cli.py stats --days 1 >> ~/ai-cost-daily.log 2>&1

# Weekly detailed report on Monday at 9 AM
0 9 * * 1 /usr/bin/python3 {data_dir}/cli.py stats --days 7 >> ~/ai-cost-weekly.log 2>&1
0 9 * * 1 /usr/bin/python3 {data_dir}/cli.py by-model --days 7 >> ~/ai-cost-weekly.log 2>&1
0 9 * * 1 /usr/bin/python3 {data_dir}/cli.py by-task --days 7 >> ~/ai-cost-weekly.log 2>&1

# Monthly cleanup on 1st at 2 AM
0 2 1 * * /usr/bin/python3 {data_dir}/cli.py cleanup --days 90 --vacuum >> ~/ai-cost-cleanup.log 2>&1

# Export backup weekly
0 3 * * 0 /usr/bin/python3 {data_dir}/cli.py export --output ~/ai-cost-backup-$(date +\\%Y\\%m\\%d).jsonl >> ~/ai-cost-backup.log 2>&1
'''.format(data_dir=str(Path(__file__).parent))
    
    def create_tool_wrapper(self, tool_name: str, original_command: str) -> str:
        """Create a wrapper script that logs LLM calls."""
        return f'''#!/bin/bash
# AI Cost Tracker - Tool Wrapper for {tool_name}
# Auto-generated wrapper

TRACKER_DIR="{Path(__file__).parent}"
DATA_DIR="${{TRACKER_DIR}}/data"

# Record start time
START_TIME=$(date +%s%3N)

# Execute original command
{original_command}
EXIT_CODE=$?

# Calculate duration
END_TIME=$(date +%s%3N)
DURATION=$((END_TIME - START_TIME))

# Log the call (adjust model and task_type as needed)
python3 "$TRACKER_DIR/log_tool_call.py" \\
    --tool "{tool_name}" \\
    --duration "$DURATION" \\
    --exit-code "$EXIT_CODE"

exit $EXIT_CODE
'''
    
    def get_dashboard_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get data formatted for dashboard display."""
        days = hours // 24
        stats = self.tracker.get_stats(days=days if days > 0 else 1)
        recent = self.tracker.get_recent_calls(limit=10, days=days if days > 0 else 1)
        
        return {
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "period_hours": hours,
            "total_calls": stats["total_calls"],
            "total_cost": stats["total_cost"],
            "cost_per_call": stats["total_calls"] / max(stats["total_cost"], 0.000001),
            "recent_calls": [
                {
                    "timestamp": call.timestamp,
                    "model": call.model,
                    "task": call.task_type,
                    "cost": call.cost_estimate
                }
                for call in recent
            ]
        }


# Tool call logger script (for cron/tool integration)
LOG_TOOL_CALL_SCRIPT = '''#!/usr/bin/env python3
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
    parser.add_argument("--task-type", default="tool", help="Task type")
    
    args = parser.parse_args()
    
    tracker = get_tracker()
    
    # Estimate tokens (can be refined based on actual usage)
    estimated_tokens_in = args.duration // 10  # Rough estimate
    estimated_tokens_out = estimated_tokens_in // 10
    
    tracker.log_call(
        model=args.model or "unknown",
        tokens_in=estimated_tokens_in,
        tokens_out=estimated_tokens_out,
        task_type=args.task_type,
        session_id=args.tool,
        extra={
            "duration_ms": args.duration,
            "exit_code": args.exit_code,
            "source": "tool_wrapper"
        }
    )
    
    print(f"✅ Logged {args.tool} call: {args.duration}ms")

if __name__ == "__main__":
    main()
'''


def install_crons():
    """Install cron jobs for automatic tracking."""
    integrator = OpenClawIntegrator()
    cron_template = integrator.create_cron_template()
    
    cron_file = Path.home() / ".ai-cost-tracker" / "openclaw-crons"
    cron_file.write_text(cron_template)
    
    print(f"✅ Cron template saved to: {cron_file}")
    print("\nTo install, run:")
    print(f"  crontab {cron_file}")
    print("\nOr manually add to your crontab:")


def create_tool_wrappers():
    """Create wrapper scripts for known tools."""
    integrator = OpenClawIntegrator()
    tools = integrator.discover_tools()
    
    wrappers_dir = Path.home() / ".ai-cost-tracker" / "wrappers"
    wrappers_dir.mkdir(parents=True, exist_ok=True)
    
    for tool in tools:
        if tool.is_llm_tool:
            wrapper = integrator.create_tool_wrapper(tool.name, f"${{HOME}}/.local/bin/{tool.name}")
            wrapper_file = wrappers_dir / tool.name
            wrapper_file.write_text(wrapper)
            wrapper_file.chmod(0o755)
    
    print(f"✅ Created {len([t for t in tools if t.is_llm_tool])} tool wrappers in: {wrappers_dir}")


def sync_from_openclaw_env():
    """Sync configuration from OpenClaw environment."""
    integrator = OpenClawIntegrator()
    config = integrator.get_llm_config()
    model = integrator.get_default_model()
    
    config_file = Path.home() / ".ai-cost-tracker" / "openclaw-config.json"
    config["default_model"] = model
    config["synced_at"] = datetime.utcnow().isoformat() + "Z"
    
    config_file.write_text(json.dumps(config, indent=2))
    
    print(f"✅ Synced OpenClaw config to: {config_file}")
    return config


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="OpenClaw integration for AI Cost Tracker",
        epilog="""
Commands:
  discover    Discover OpenClaw tools
  sync        Sync config from OpenClaw
  crons       Generate cron template
  wrappers    Create tool wrappers
  report      Generate OpenClaw report
  dashboard   Get dashboard data
        """
    )
    
    parser.add_argument("command", choices=[
        "discover", "sync", "crons", "wrappers", "report", "dashboard"
    ])
    parser.add_argument("--days", type=int, default=7, help="Days for report")
    parser.add_argument("--hours", type=int, default=24, help="Hours for dashboard")
    
    args = parser.parse_args()
    
    integrator = OpenClawIntegrator()
    
    if args.command == "discover":
        tools = integrator.discover_tools()
        print(f"\n📦 Discovered {len(tools)} tools:")
        for tool in tools[:20]:
            llm_indicator = "🤖" if tool.is_llm_tool else "📄"
            print(f"  {llm_indicator} {tool.name}")
        if len(tools) > 20:
            print(f"  ... and {len(tools) - 20} more")
    
    elif args.command == "sync":
        config = sync_from_openclaw_env()
        print(f"\n✅ Synced {len(config)} config values")
    
    elif args.command == "crons":
        cron_template = integrator.create_cron_template()
        print(cron_template)
        install_crons()
    
    elif args.command == "wrappers":
        create_tool_wrappers()
    
    elif args.command == "report":
        report = integrator.generate_openclaw_report(days=args.days)
        print(json.dumps(report, indent=2))
    
    elif args.command == "dashboard":
        data = integrator.get_dashboard_data(hours=args.hours)
        print(json.dumps(data, indent=2))
