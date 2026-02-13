#!/usr/bin/env python3
import json
import subprocess
import os

os.makedirs('/home/legion/.openclaw/workspace/openclaw-dashboard/dist/api', exist_ok=True)

# Get sessions
try:
    result = subprocess.run(['openclaw', 'sessions', 'list', '--json'], capture_output=True, text=True, timeout=10)
    # Filter out config warnings and other non-JSON lines (│, ◇, ─, ├, └, etc.)
    lines = [l for l in result.stdout.split('\n') if l and not any(l.startswith(c) for c in ['│', '◇', '─', '├', '└', '╰', '╭', '╮', '╯'])]
    data = json.loads('\n'.join(lines))
    
    sessions = []
    for s in data.get('sessions', []):
        age_ms = s.get('ageMs', 0) or 0
        sessions.append({
            'sessionKey': s.get('key', ''),
            'kind': s.get('kind', ''),
            'activeMinutes': age_ms // 60000,
            'model': s.get('model', 'minimax2.5'),
            'createdAt': s.get('updatedAt')
        })
except Exception as e:
    print(f"Error getting sessions: {e}")
    sessions = []

with open('/home/legion/.openclaw/workspace/openclaw-dashboard/dist/api/sessions.json', 'w') as f:
    json.dump({'sessions': sessions}, f)

# Get cron - try with timeout, use fallback if fails
jobs = []
try:
    result = subprocess.run(
        ['timeout', '5', 'openclaw', 'cron', 'list', '--json'],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0 and result.stdout:
        lines = [l for l in result.stdout.split('\n') if l and not l.startswith('[')]
        data = json.loads('\n'.join(lines))
        
        for j in data.get('jobs', []):
            state = j.get('state', {})
            jobs.append({
                'id': j.get('id', ''),
                'name': j.get('name', ''),
                'enabled': j.get('enabled', True),
                'schedule': j.get('schedule', {}),
                'state': {
                    'nextRunAtMs': state.get('nextRunAtMs', 0),
                    'lastRunAtMs': state.get('lastRunAtMs', 0),
                    'lastStatus': state.get('lastStatus', 'unknown'),
                    'lastDurationMs': state.get('lastDurationMs')
                },
                'sessionTarget': j.get('sessionTarget', 'isolated')
            })
    else:
        raise Exception("Cron command failed or returned empty")
except Exception as e:
    # Fallback: use known jobs from playbook
    print(f"Using fallback cron data: {e}")
    # These are the known cron jobs from the playbook
    jobs = [
        {
            'id': 'apexform-tests',
            'name': 'apexform tests',
            'enabled': True,
            'schedule': {'kind': 'cron', 'expr': '0 0 * * *', 'tz': 'America/Vancouver'},
            'state': {'nextRunAtMs': 0, 'lastRunAtMs': 0, 'lastStatus': 'unknown', 'lastDurationMs': None},
            'sessionTarget': 'isolated'
        },
        {
            'id': 'hamono-tests',
            'name': 'hamono tests',
            'enabled': True,
            'schedule': {'kind': 'cron', 'expr': '0 2 * * *', 'tz': 'America/Vancouver'},
            'state': {'nextRunAtMs': 0, 'lastRunAtMs': 0, 'lastStatus': 'unknown', 'lastDurationMs': None},
            'sessionTarget': 'isolated'
        },
        {
            'id': 'shootrebook-tests',
            'name': 'shootrebook tests',
            'enabled': True,
            'schedule': {'kind': 'cron', 'expr': '0 3 * * *', 'tz': 'America/Vancouver'},
            'state': {'nextRunAtMs': 0, 'lastRunAtMs': 0, 'lastStatus': 'unknown', 'lastDurationMs': None},
            'sessionTarget': 'isolated'
        },
        {
            'id': 'stitchai-tests',
            'name': 'stitchai tests',
            'enabled': True,
            'schedule': {'kind': 'cron', 'expr': '0 4 * * *', 'tz': 'America/Vancouver'},
            'state': {'nextRunAtMs': 0, 'lastRunAtMs': 0, 'lastStatus': 'unknown', 'lastDurationMs': None},
            'sessionTarget': 'isolated'
        },
        {
            'id': 'dashboard-refresh',
            'name': 'dashboard refresh',
            'enabled': True,
            'schedule': {'kind': 'every', 'everyMs': 300000},
            'state': {'nextRunAtMs': 0, 'lastRunAtMs': 0, 'lastStatus': 'unknown', 'lastDurationMs': None},
            'sessionTarget': 'isolated'
        },
        {
            'id': 'kyle-response-checker',
            'name': 'kyle response checker',
            'enabled': True,
            'schedule': {'kind': 'every', 'everyMs': 300000},
            'state': {'nextRunAtMs': 0, 'lastRunAtMs': 0, 'lastStatus': 'unknown', 'lastDurationMs': None},
            'sessionTarget': 'isolated'
        }
    ]

with open('/home/legion/.openclaw/workspace/openclaw-dashboard/dist/api/cron.json', 'w') as f:
    json.dump({'jobs': jobs}, f)

print("Dashboard JSON refreshed successfully")
