# Cron Job Definitions – Operations Playbook

| Job Name | Schedule (Pacific Time) | Repository / Target | Purpose / Payload Summary |
|----------|------------------------|---------------------|---------------------------|
| **apexform – Midnight** | `0 0 * * *` (midnight) | `apexform` | **PHASE 1:** Pull changes, run tests/lint, fix bugs, create PRs. **PHASE 2 (CHAOS):** Form abuse, workout tracking torture, subscription edge cases. Kyle reviews/merges PRs. |
| **hamono – 2 AM** | `0 2 * * *` (2:00 AM) | `hamono` | **PHASE 1:** Fix issues, test, PR. **PHASE 2 (CHAOS):** Navigation lock testing, state abuse, PWA torture, rapid input spam, network brutality. |
| **shootrebook – 3 AM** | `0 3 * * *` (3:00 AM) | `shootrebook` | **PHASE 1:** Fix issues, test, PR. **PHASE 2 (CHAOS):** Booking flow abuse, payment chaos, calendar sync torture, auth edge cases. |
| **stitchai – 4 AM** | `0 4 * * *` (4:00 AM) | `stitchai` | **PHASE 1:** Fix issues, test, PR. **PHASE 2 (CHAOS):** AI rate limiting, session chaos, auth expiry, message flooding, context overflow. |

## Nightly CHAOS Testing (NEW)

All repository jobs now include a **"break-everything" chaos phase** after regular maintenance. This adversarial testing finds bugs users hit in the wild.

### CHAOS Testing Categories

| Category | Description |
|----------|-------------|
| **Navigation Chaos** | Rapid page switching, back/forward abuse, refresh at critical moments, deep linking |
| **State Inconsistency** | Resource maxing/depletion, simultaneous actions, time skip, offline/online switches |
| **Input Torture** | Spam-clicking (100+ times), long press, drag abuse, pinch zoom, rotation |
| **Edge Cases** | Empty lists, zero states, max level, tutorial interruption, purchase abandonment |
| **Network Brutality** | Wifi kill mid-save, 3G throttling, offline during critical actions, server timeouts |
| **PWA Abuse** | Install/uninstall cycles, browser data clear, update while running, cache corruption |
| **Auth & Security** | Session expiry, token refresh loops, concurrent sessions, permission escalation |

### Bug Handling
- Each bug found → Screenshot + exact repro steps → GitHub issue created
- Severity tagged: crash / data loss / UI broken / minor
- Summary posted after each chaos run
| **Morning-Brief (Isolated)** | `0 9 * * *` (9:00 AM) - *example* | `isolated` session | Creates a fresh isolated session to deliver pending system events/notifications. Uses `sessionTarget: "isolated"` with `agentTurn` payload. |
| **Research / Ad-hoc** | Variable | Various | Used for ad-hoc research, model testing, or ad-hoc script execution. Payload is an `agentTurn` with a custom prompt. |

**Common Payload Structure (isolated sessions)**
```json
{
  "kind": "agentTurn",
  "message": "<human-readable description of the task>",
  "model": "default",
  "timeoutSeconds": 600
}
```

**Delivery** - All jobs use `delivery.mode: "announce"` so the result is posted back to the originating channel.

**Notes for Maintenance**

- Schedules are expressed in UTC-offseted cron syntax (`America/Vancouver`).
- If you need to adjust a schedule, edit the corresponding cron entry via `openclaw cron update`.
- Each job logs its output; failures are captured in the cron logs for later review.

---

*Keep this file handy when adding, removing, or modifying scheduled tasks.*