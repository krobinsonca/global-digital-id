#!/bin/bash
# Signal Collector - Gathers data from all sources
# Usage: ./collect_all.sh [date]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"
DATE="${1:-$(date +%Y-%m-%d)}"

mkdir -p "$DATA_DIR/$DATE"

log() { echo "[$(date '+%H:%M:%S')] Collecting: $1"; }

# Collect git status for all repos
collect_git_status() {
    log "Git status for all repos..."
    for repo in hamono shootrebook stitchai apexform; do
        REPO_PATH="/home/legion/.openclaw/workspace/$repo"
        if [ -d "$REPO_PATH/.git" ]; then
            cd "$REPO_PATH"
            git status --short > "$DATA_DIR/$DATE/${repo}_git_status.txt" 2>/dev/null || echo "Error" > "$DATA_DIR/$DATE/${repo}_git_status.txt"
            git log --oneline -5 > "$DATA_DIR/$DATE/${repo}_recent_commits.txt" 2>/dev/null || echo "Error" > "$DATA_DIR/$DATE/${repo}_recent_commits.txt"
        fi
    done
}

# Collect test results
collect_test_results() {
    log "Test results..."
    
    # Hamono tests
    if [ -f "/home/legion/.openclaw/workspace/hamono/test_results.txt" ]; then
        cp "/home/legion/.openclaw/workspace/hamono/test_results.txt" "$DATA_DIR/$DATE/hamono_tests.txt"
    fi
    
    # Nightly maintenance data
    if [ -f "/home/legion/.openclaw/workspace/hamono/nightly-maintenance-$DATE.json" ]; then
        cp "/home/legion/.openclaw/workspace/hamono/nightly-maintenance-$DATE.json" "$DATA_DIR/$DATE/hamono_nightly.json"
    fi
}

# Collect cron history
collect_cron_status() {
    log "Cron status..."
    crontab -l > "$DATA_DIR/$DATE/crontab.txt" 2>/dev/null || echo "No crontab" > "$DATA_DIR/$DATE/crontab.txt"
    
    # Check system cron logs
    if [ -f "/var/log/syslog" ]; then
        grep -i "cron\|crond" "/var/log/syslog" | tail -50 > "$DATA_DIR/$DATE/cron_recent.log" 2>/dev/null || true
    fi
}

# Collect issue/PR data from GitHub (placeholder for API integration)
collect_github_data() {
    log "GitHub data..."
    # Placeholder - would integrate with gh CLI or GitHub API
    echo "GitHub collection ready for API integration" > "$DATA_DIR/$DATE/github_status.txt"
}

# Collect system health
collect_system_health() {
    log "System health..."
    {
        echo "=== System Health - $DATE ==="
        echo "Uptime: $(uptime)"
        echo "Memory: $(free -h 2>/dev/null || echo 'N/A')"
        echo "Disk: $(df -h /home/legion/.openclaw/workspace 2>/dev/null || echo 'N/A')"
        echo "Running processes: $(ps aux --no-headers | wc -l)"
    } > "$DATA_DIR/$DATE/system_health.txt"
}

# Generate summary manifest
generate_manifest() {
    log "Generating manifest..."
    {
        echo "=== Signal Collection Manifest - $DATE ==="
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "Collected files:"
        ls -la "$DATA_DIR/$DATE/" | tail -n +4
        echo ""
        echo "Data quality:"
        echo "  Git repos checked: $(ls -d "$DATA_DIR/$DATE"/*_git_status.txt 2>/dev/null | wc -l)"
        echo "  Test results: $(ls "$DATA_DIR/$DATE"/*tests*.txt 2>/dev/null | wc -l)"
        echo "  Cron status: $([ -f "$DATA_DIR/$DATE/crontab.txt" ] && echo 'OK' || echo 'Missing')"
    } > "$DATA_DIR/$DATE/manifest.txt"
}

# Main execution
echo "=== Signal Collection - $DATE ==="
collect_git_status
collect_test_results
collect_cron_status
collect_github_data
collect_system_health
generate_manifest

echo "Collection complete. Files in: $DATA_DIR/$DATE/"
ls "$DATA_DIR/$DATE/"
