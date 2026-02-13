### PR Process for ApexForm (krobinsonca/apexform) (2026-02-10)
**Rule:** Merge simple PRs directly (syntax, small UI fixes). For non-simple (features, complex): Add Kyle (krobinsonca) as reviewer + request review.
**Source:** Kyle instruction 2026-02-10.
**Examples:** Simple: syntax errors (#338), clipboard (#339). Non-simple: UI overhauls, new features (#299 timer UI).

### Email Access & Work Streams (2026-02-10)
**Email:** Use Graph API (`node email.js check/refresh`), NOT himalaya CLI (basic auth blocked).

**Three Work Streams:**
1. **Photography:** Lakehill Baseball/Softball, Victoria Grizzlies Hockey, GotPhoto/Stripe platform
2. **Software:** ApexForm (Flutter), Hamono (Flutter game), ShootRebook (React), StitchAI (React+AI)
3. **AI Services:** Anthropic, Moonshot, ElevenLabs, NVIDIA

**Key Contacts:** david@victoriagrizzlies.com (hockey client), sjjalford@gmail.com (personal)

### Phone Connectivity Issues (2026-02-11)
**WhatsApp:** QR linking fails with 408 timeout. Command: `openclaw channels login --channel whatsapp --verbose`. Workaround: scan QR quickly or use phone WhatsApp > Linked Devices first.

**Telegram:** 401 "User not found" = bot can't see the user. Fix flow:
1. Phone Telegram > @LegionScorpionBot > START button > send "hi"
2. Laptop: `openclaw logs --follow` to watch for inbound
3. If persist: BotFather > /mybots > LegionScorpionBot > Group Privacy > Disable (already done)

**Tailscale Webchat:** Phone Tailscale app > connect > browser `https://100.77.235.87:18789` > auth token.

### GitHub Best Practices (2026-02-11)
**File:** memory/github-best-practices.md – Branching, commits, PRs (ApexForm rule), protection, CI/CD, releases, gh CLI.

### Memory Plugin Status (2026-02-11)
**Prior Error:** `401 Incorrect API key provided: ${OPENAI_API_KEY}` — env var not resolved. **Fix:** Update `/home/legion/.openclaw/openclaw.json` with actual API key in `plugins.entries["memory-lancedb"].config.embedding.apiKey`.

**Current Issue:** memory-lancedb fails to load: Cannot find module '@lancedb/lancedb'. Install deps: `cd /home/legion/.npm-global/lib/node_modules/openclaw/extensions/memory-lancedb && npm install`.

### Model Limits: Minimax (2026-02-11, Updated 2026-02-12)
**openrouter/minimax/minimax-m2.1:** Paid coding plan subscription. 300 prompts per 5 hours. Reserve for critical coding/heavy reasoning tasks only. Prioritize free models (nemotron, etc.).
**openrouter/minimax/minimax-m2.5:** Now default model (alias: `minimax2.5`). Updated all 4 cron jobs to use minimax2.5.

### Multi-Telegram Bot Setup (2026-02-12)
**Pattern:** Use `channels.telegram.accounts` object for multiple bots:
```json
{
  "channels": {
    "telegram": {
      "accounts": {
        "main": { "name": "LegionMainBot", "botToken": "..." },
        "config": { "name": "LegionConfigBot", "botToken": "..." }
      }
    }
  }
}
```
**Lesson:** Always check official docs first for config tasks.

### Systems Built (2026-02-12)
1. **AI Cost Tracker** - `/home/legion/.openclaw/workspace/ai-cost-tracker/` - CLI cost logging, 28-model pricing
2. **Nightly Business Briefing** - Multi-AI council (LeadAnalyst + 4 personas), playbook-integrated
3. **RAG Knowledge Base** - `/home/legion/.openclaw/workspace/rag-kb/` - Auto-indexes `knowledge/playbook/*.md`

### Hamono Cron Issues (2026-02-12, Updated 2026-02-12)
- Gateway timeouts due to memory-lancedb crash (FIXED)
- Flutter not in sandbox PATH - tests skipped (workaround: use full path)
- Test coverage at 15-20% (177 pass, ~35 fail)
- 6 feature issues open (#23-27)
- **Issue:** Agent not creating PRs for features - playing it safe citing "architectural decisions needed"
- **Note:** Per playbook, agents SHOULD implement features and create PRs. Kyle reviews/merges, not pre-approves.

### Gateway Instability (2026-02-12)
- memory-lancedb errors: "Cannot find module '@lancedb/lancedb'"
- Fix: `openclaw doctor --fix` cleaned config
- Root cause: `package.json` had `openclaw: "workspace:*"` blocking npm install
- Resolution: Changed to `file:..`, ran `npm install` (33 packages added)

### Auto-Develop Model (2026-02-12)
**Core Philosophy**: Agents act as developers. Fix bugs, implement features, test, create PRs. Kyle reviews/merges PRs.

**Rules**:
- Bugs & Issues: Fix automatically, test, create PR
- Features: Implement solution, test, create PR
- Trivial Fixes: Commit directly, no PR needed
- Minor PRs (linting): Fix, test, merge automatically
- Major PRs: Create PR, Kyle reviews/merges

**Workflow**: Investigate → Implement → Test → Commit → PR → Notify Kyle

### LanceDB False "Unavailable" Status (2026-02-12)
**Finding:** OpenClaw Bug #8921 - memory-lancedb shows "unavailable" in `openclaw status` but works perfectly.
- Verification: `openclaw plugins list` shows "loaded", `openclaw ltm stats` returns count, `openclaw ltm search` works
- Root cause: Status command hardcodes health probe for `memory-core` only; non-core plugins skipped
- Impact: False negative status UI; plugin fully functional
- Workaround: Use `openclaw ltm stats/list/search` CLI commands to verify

### Telegram StreamMode Account Override (2026-02-12)
**Issue:** `streamMode: "block"` at top-level ignored; messages still fragmented.
**Root cause:** `channels.telegram.accounts.main.streamMode` and `accounts.config.streamMode` override top-level.
**Fix:** Set `"streamMode": "block"` on both `main` and `config` account objects.
**Restart required:** `openclaw gateway restart` after config change.

### Telegram Fragmentation Unresolved (2026-02-12)
**Problem:** Messages STILL fragment despite `streamMode: "off"` at all levels (top-level + accounts).
**Tried:** `partial` → `block` → `off` - no change.
**Suspected causes:** Block streaming at agent level, message queue settings, or deeper OpenClaw bug.
**Next step:** Search OpenClaw issues or try clean restart without streaming configs.

### Config Validation is Strict (2026-02-12)
**Mistake:** Added `blockStreaming: true` (should be `"on"`/`"off"`) and `blockStreamingDefault: "off"`.
**Result:** Gateway crashed on restart.
**Fix:** Reverted via `openclaw doctor --non-interactive`.
**Rule:** Always verify config values against official docs before adding. Invalid values crash gateway.