# GitHub Webhook Bridge

A bridge between GitHub and OpenClaw agents that enables **asynchronous decision loops** with Kyle via Telegram.

## The Problem

Agents can't wait indefinitely for architectural decisions. When they hit blockers:

```
Agent: "I need to know which backend to use for Guild System"
→ Traditional: Agent stalls, waits for human
→ New Flow: Agent tags Kyle, continues other work, resumes when Kyle responds
```

## The Solution

```
1. Agent creates issue tagging @Scorpion23ca
2. GitHub webhook → Telegram notification
3. Kyle responds in GitHub
4. Webhook → Agent notified and resumes work
```

## Quick Start

### 1. Start the Webhook Bridge

```bash
cd /home/legion/.openclaw/workspace/webhook-bridge
npm install
npm start 3000
```

### 2. Configure GitHub Webhooks

For each repo (apexform, hamono, shootrebook, stitchai):

1. Go to **Settings → Webhooks → Add webhook**
2. **Payload URL**: `http://YOUR_IP:3000/webhook`
3. **Content type**: `application/json`
4. **Secret**: (optional, set `WEBHOOK_SECRET` env var)
5. **Events**: Select `Issues` and `Issue comments`

### 3. Configure Telegram Notifications

Set environment variables:
```bash
export TELEGRAM_BOT_TOKEN="your-bot-token"
export TELEGRAM_CHAT_ID="7162874831"
```

### 4. Agent Usage

When an agent needs Kyle's input:

```bash
# Tag Kyle in existing issue
node tag-kyle.js --repo krobinsonca/hamono --issue 23 \
  "Should we use Firebase or Supabase for the Guild System backend?"

# Create new issue tagging Kyle
node tag-kyle.js --repo krobinsonca/hamono --create \
  --title="Guild System Architecture Decision" \
  --body="Need input on backend choice..."
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│   GitHub     │────▶│ Webhook      │────▶│ Telegram   │
│  Issue/PR    │     │ Bridge       │     │ (Kyle)     │
└─────────────┘     └──────────────┘     └────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   OpenClaw   │
                    │   Session    │
                    │   Resumer    │
                    └──────────────┘
```

## Files

- `server.js` - Express server handling GitHub webhooks
- `tag-kyle.js` - CLI for agents to tag Kyle in issues
- `README.md` - This file

## Environment Variables

| Variable | Description |
|----------|-------------|
| `WEBHOOK_SECRET` | GitHub webhook secret for signature verification |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Telegram chat ID for Kyle (7162874831) |

## Deployment

Run the bridge locally and expose via **Tailscale Funnel**:

```bash
# Start the bridge
cd /home/legion/.openclaw/workspace/webhook-bridge
npm start 3000

# Expose via Tailscale (run in separate terminal)
tailscale serve https://localhost:3000 on

# Or use Funnel for a truly public URL
tailscale funnel 3000
```

Make sure Tailscale is running and you've enabled funnel access in your Tailscale admin.

**Note:** Replace `YOUR_IP` in GitHub webhook URLs with your Tailscale URL (e.g., `https://your-machine.ts.net:3000/webhook`).

## Agent Playbook Integration

Per the Operations Playbook, agents should:

1. **Hit a blocker requiring Kyle's input**
2. **Tag Kyle in a GitHub issue** using `tag-kyle.js`
3. **Continue with other work**
4. **Resume when notified** via webhook (future enhancement)

This ensures agents stay productive while waiting for decisions.

## Kyle's Response Flow

When Kyle responds to a tagged issue:

1. GitHub sends webhook event
2. Bridge detects Kyle's comment
3. (Future) Bridge triggers agent session to resume work
4. Agent continues implementation

## Troubleshooting

**No notifications received?**
- Check webhook delivery logs in GitHub Settings
- Verify Telegram bot token and chat ID
- Check bridge logs: `npm start` output

**Webhook not hitting bridge?**
- Ensure port 3000 is accessible
- Check firewall settings
- Verify webhook URL is publicly reachable

**Token errors?**
- Run `gh auth status` to verify GitHub CLI authentication
- Export `GITHUB_TOKEN` environment variable
