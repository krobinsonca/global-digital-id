# Cron Job Definitions – Operations Playbook

| Job Name | Schedule (Pacific Time) | Repository / Target | Purpose / Payload Summary |
|----------|------------------------|---------------------|---------------------------|
| **apexform – Midnight** | `0 0 * * *` (midnight) | `apexform` | Pull changes, run tests/lint, **fix bugs**, create PRs, push. Kyle reviews/merges PRs. Keep workspace persistent. |
| **hamono – 2 AM** | `0 2 * * *` (2:00 AM) | `hamono` | Same as apexform: fix issues, test, PR, push. Isolated to avoid overlap. |
| **shootrebook – 3 AM** | `0 3 * * *` (3:00 AM) | `shootrebook` | Same: fix issues, test, PR, push. One hour after apexform to space rate limits. |
| **stitchai – 4 AM** | `0 4 * * *` (4:00 AM) | `stitchai` | Same: fix issues, test, PR, push. One hour after shootrebook. |
| **Morning‑Brief (Isolated)** | `0 9 * * *` (9:00 AM) – *example* | `isolated` session | Creates a fresh isolated session to deliver pending system events/notifications. Uses `sessionTarget: "isolated"` with `agentTurn` payload. |
| **Research / Ad‑hoc** | Variable | Various | Used for ad‑hoc research, model testing, or ad‑hoc script execution. Payload is an `agentTurn` with a custom prompt. |

**Common Payload Structure (isolated sessions)**  
```json
{
  "kind": "agentTurn",
  "message": "<human‑readable description of the task>",
  "model": "default",
  "timeoutSeconds": 600
}
```

**Delivery** – All jobs use `delivery.mode: "announce"` so the result is posted back to the originating channel.

**Notes for Maintenance**  

- Schedules are expressed in UTC‑offseted cron syntax (`America/Vancouver`).  
- If you need to adjust a schedule, edit the corresponding cron entry via `openclaw cron update`.  
- Each job logs its output; failures are captured in the cron logs for later review.  

---  

*Keep this file handy when adding, removing, or modifying scheduled tasks.* 