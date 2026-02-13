# AI Cost Tracker

Track and report LLM API usage and costs across Anthropic, OpenAI, Google, xAI, and more.

## Features

- 📊 **Log every LLM call** with timestamp, model, tokens, task type, and cost estimate
- 💰 **Pricing tables** for Anthropic, OpenAI, Google, xAI, DeepSeek, and OpenRouter
- 📁 **JSONL storage** for easy backup and analysis
- 📈 **Reports** with filters: `--days`, `--model`, `--task`
- 🗄️ **SQLite database** for fast queries
- 🔧 **OpenClaw integration** for cron jobs and tool wrappers

## Installation

```bash
# Clone and install
cd ai-cost-tracker
pip install -e .

# Or just add to PATH
export PATH="$PATH:/path/to/ai-cost-tracker"
```

## Quick Start

```bash
# Log a call manually
python quick_log.py gpt-4o 1000 500 coding

# View statistics
python cli.py stats

# List all models with pricing
python cli.py models

# View recent calls
python cli.py recent

# Get daily breakdown
python cli.py daily

# Get cost by model
python cli.py by-model

# Get cost by task type
python cli.py by-task

# Estimate cost for a hypothetical call
python cli.py estimate --model gpt-4o --prompt-tokens 10000 --completion-tokens 5000

# Export data to JSONL
python cli.py export --output backup.jsonl

# Import from JSONL
python cli.py import --input backup.jsonl

# Clean up old records (older than 90 days)
python cli.py cleanup --days 90 --vacuum
```

## Programmatic Usage

```python
from ai_cost_tracker import CostTracker, PricingEngine

# Initialize tracker
tracker = CostTracker()

# Log a call
call = tracker.log_call(
    model="gpt-4o",
    tokens_in=1500,
    tokens_out=500,
    task_type="coding"
)

# Get statistics
stats = tracker.get_stats(days=7)  # Last 7 days
print(f"Weekly cost: ${stats['total_cost']:.4f}")

# Get model breakdown
models = tracker.get_model_breakdown(days=30)

# Get daily costs
daily = tracker.get_daily_costs(days=30)
```

## Pricing

All pricing is stored in `pricing.json` and automatically updated. Current providers:

| Provider | Models |
|----------|--------|
| **Anthropic** | Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus, Claude 3 Haiku, Claude 4 |
| **OpenAI** | GPT-4o, GPT-4o Mini, GPT-4 Turbo, GPT-4, GPT-3.5 Turbo, o1, o1-mini, o3-mini |
| **Google** | Gemini 2.0 Flash, Gemini 1.5 Flash, Gemini 1.5 Pro, Gemini 1.0 Pro |
| **xAI** | Grok 3, Grok 3 Mini, Grok 2, Grok 2 Mini, Grok Beta |
| **DeepSeek** | DeepSeek Chat V3, DeepSeek Reasoner |
| **OpenRouter** | Various free models |

## OpenClaw Integration

```bash
# Generate cron template
python openclaw_integration.py crons

# Discover OpenClaw tools
python openclaw_integration.py discover

# Sync config from OpenClaw
python openclaw_integration.py sync

# Generate OpenClaw report
python openclaw_integration.py report --days 7

# Get dashboard data
python openclaw_integration.py dashboard --hours 24
```

## File Structure

```
ai-cost-tracker/
├── __init__.py           # Package init
├── tracker.py            # Core tracking logic
├── cli.py                # CLI reporter
├── pricing.json          # Pricing tables
├── openclaw_integration.py  # OpenClaw integration
├── log_tool_call.py      # Tool wrapper script
├── quick_log.py          # Quick logging utility
├── examples.py           # Usage examples
├── setup.py              # Setup script
└── README.md             # This file
```

## Data Location

Default data directory: `~/.ai-cost-tracker/`

```
~/.ai-cost-tracker/
├── ai_costs.db           # SQLite database
├── llm_calls.jsonl       # JSONL log file
└── export.jsonl          # Exported data (when created)
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GOOGLE_API_KEY` | Google API key |
| `DEFAULT_MODEL` | Default model for logging |

## License

MIT
