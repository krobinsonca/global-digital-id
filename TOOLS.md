# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

### MCP Servers

- **minimax** - Coding Plan MCP (web_search + understand_image)
  - Config: `/home/legion/.mcporter/mcporter.json`
  - Key: `sk-cp-EJK4hbllIhx7qxKA6DDoE318RGGNxhf2M4NXEZB21ulThX5P2fVAXyxXKXY_GMYU9or38JSH90J4AsE5QSH5_tWU0xobDeUzQVN1-mm24cdKHkOS1sasCzU`
  - Uses: `mcporter call minimax.web_search` and `mcporter call minimax.understand_image`

### Local LLM Server

- **URL**: http://100.79.11.85:1234/v1
- **API Key**: `sk-lm-chFa7gfb:EwQdBNgNNqRmAXZiqUj8`
- **Models**:
  - `gemma` → google/gemma-3-4b
  - `deepseek-r1` → deepseek/deepseek-r1-0528-qwen3-8b
  - `qwen-vl` → qwen/qwen3-vl-8b
- **Configured in**: openclaw.json under `models.providers.local-llm`

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
