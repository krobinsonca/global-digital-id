# Nightly Business Briefing System

## Overview
Automated nightly digest combining multi-AI persona analysis with signals from repos, tests, and crons to produce ranked recommendations.

## Architecture

### Phases

#### Phase 1: Signal Collection & Draft
- **Collector**: Gathers data from all monitored sources
- **LeadAnalyst**: Synthesizes raw signals into initial draft

#### Phase 2: Parallel Reviews
All 5 personas review independently:
- **GrowthStrategist**: Growth opportunities, market positioning
- **RevenueGuardian**: Cost efficiency, monetization, resource allocation
- **SkepticalOperator**: Risk assessment, technical debt, reliability
- **TeamDynamicsArchitect**: Process health, capacity, collaboration
- **LeadAnalyst**: Final synthesis and consensus building

#### Phase 3: Consensus & Ranking
- Aggregate reviews
- Score recommendations by: **Impact × Confidence / Effort**
- Generate final prioritized action list

### Personas

| Persona | Focus | Output |
|---------|-------|--------|
| LeadAnalyst | Synthesis, orchestration | Draft + final summary |
| GrowthStrategist | Opportunities, expansion | Growth recommendations |
| RevenueGuardian | Efficiency, costs, revenue | Resource optimization |
| SkepticalOperator | Risks, debt, stability | Technical health score |
| TeamDynamicsArchitect | Process, capacity, morale | Team capacity analysis |

### Signal Sources

```
SIGNALS/
├── repos/
│   ├── hamono/          # Flutter game project
│   │   ├── git_status
│   │   ├── test_results
│   │   └── nightly_maintenance.json
│   ├── shootrebook/     # Firebase project
│   │   ├── test_results
│   │   └── integration_status
│   ├── stitchai/        # AI project
│   │   └── status
│   └── apexform/        # Fitness platform
│       └── build_status
├── tests/
│   ├── flutter/
│   ├── integration/
│   └── e2e/
├── crons/
│   ├── smoke_tests
│   ├── maintenance
│   └── backup/
└── system/
    └── health_metrics
```

## Quick Start

```bash
# Run full briefing pipeline
./business-briefing.sh run

# Run with specific date
./business-briefing.sh run 2026-02-12

# Generate report only
./business-briefing.sh report

# Setup cron (runs at 2 AM nightly)
./business-briefing.sh install-cron
```

## Output

Generated reports in `output/YYYY-MM-DD/`:
- `briefing_draft.md` - Initial analysis
- `briefing_reviews.json` - All persona reviews
- `briefing_consensus.md` - Final consensus report
- `recommendations_ranked.md` - Prioritized action list

## Ranking Formula

```
Score = (Impact × Confidence) / Effort

Where:
- Impact: 1-5 (1=low, 5=critical)
- Confidence: 0.0-1.0 (evidence strength)
- Effort: 1-5 (1=trivial, 5=massive)
```

## Cron Configuration

```bash
# Add to crontab
0 2 * * * /home/legion/.openclaw/workspace/business-briefing/business-briefing.sh run >> /var/log/business-briefing.log 2>&1
```

## Files

- `personas/` - AI persona configurations
- `collectors/` - Signal gathering scripts
- `processor/` - Analysis and ranking engine
- `templates/` - Report templates
- `cron/` - Cron job configuration
