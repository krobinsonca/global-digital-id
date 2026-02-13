#!/bin/bash
# Nightly Business Briefing - Main Orchestrator
# Usage: ./business-briefing.sh [command] [date]
# Commands: run, report, install-cron, status
# Date format: YYYY-MM-DD (default: today)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATE="${2:-$(date +%Y-%m-%d)}"
OUTPUT_DIR="$SCRIPT_DIR/output/$DATE"
LOG_DIR="$SCRIPT_DIR/logs"
DATA_DIR="$SCRIPT_DIR/data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() { echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }

# Ensure directories exist
mkdir -p "$OUTPUT_DIR" "$LOG_DIR" "$DATA_DIR"

case "$1" in
    run)
        log "Starting Nightly Business Briefing for $DATE"
        
        # Phase 1: Signal Collection
        log "Phase 1: Collecting signals..."
        bash "$SCRIPT_DIR/collectors/collect_all.sh" "$DATE"
        
        # Phase 2: Generate Draft
        log "Phase 2: Generating draft analysis..."
        bash "$SCRIPT_DIR/processor/generate_draft.sh" "$DATE"
        
        # Phase 3: Parallel Reviews
        log "Phase 3: Running parallel persona reviews..."
        bash "$SCRIPT_DIR/processor/run_reviews.sh" "$DATE"
        
        # Phase 4: Consensus & Ranking
        log "Phase 4: Building consensus and ranking recommendations..."
        bash "$SCRIPT_DIR/processor/build_consensus.sh" "$DATE"
        
        success "Briefing complete. Output: $OUTPUT_DIR"
        ;;
    
    report)
        log "Generating report for $DATE..."
        bash "$SCRIPT_DIR/processor/generate_report.sh" "$DATE"
        ;;
    
    install-cron)
        log "Installing nightly cron job..."
        CRON_JOB="0 2 * * * $SCRIPT_DIR/business-briefing.sh run >> $LOG_DIR/cron.log 2>&1"
        (crontab -l 2>/dev/null | grep -v "business-briefing.sh"; echo "$CRON_JOB") | crontab -
        success "Cron installed (runs at 2 AM daily)"
        ;;
    
    status)
        echo "=== Business Briefing Status ==="
        echo "Date: $DATE"
        echo "Output Dir: $OUTPUT_DIR"
        echo "Last Run: $(stat -c %y "$LOG_DIR/cron.log" 2>/dev/null || echo 'Never')"
        echo ""
        echo "Available reports:"
        ls -la "$SCRIPT_DIR/output/" 2>/dev/null || echo "No reports yet"
        ;;
    
    *)
        echo "Usage: $0 {run|report|install-cron|status} [date]"
        echo ""
        echo "Commands:"
        echo "  run          - Run full briefing pipeline"
        echo "  report       - Generate report from existing data"
        echo "  install-cron - Install nightly cron job (2 AM)"
        echo "  status       - Show system status"
        exit 1
        ;;
esac
