# Memory System – Operations Playbook

## 1. Overview

The memory system stores persistent knowledge in two complementary layers:

1. **Built‑in OpenClaw Embeddings** – lightweight vector store tied to `MEMORY.md` and `memory/*.md` files.  
2. **LanceDB Plugin** – optional on‑disk SQLite‑vec extension for richer similarity search.

## 2. Current State (as of 2026‑02‑11)

| Item | Status |
|------|--------|
| **Memory Plugin** | Enabled and functional (`plugins.slots.memory = "memory-lancedb"`). |
| **LanceDB Load** | Previously failed with `Cannot find module '@lancedb/lancedb'`. Fixed by installing the extension (`npm install @lancedb/lancedb`). |
| **Embedding API Key** | Patched into `openclaw.json` under `plugins.entries.memory-lancedb.config.embedding.apiKey`. |
| **Auto‑Capture** | Enabled – important messages are automatically captured into the QMD side‑car. |
| **Auto‑Recall** | Enabled – relevant memories are injected into context on demand. |

## 3. Directory Layout

```
/home/legion/.openclaw/workspace/memory/
├─ MEMORY.md                 ← Global quick‑reference log
├─ 2026-02-05.md
├─ 2026-02-06.md
├─ … (daily logs)
├─ github-best-practices.md
├─ issue-creation-guidelines.md
├─ issue-logging-rule.md
└─ … (topic‑specific markdown files)
```

- Each `YYYY‑MM‑DD.md` file is a **daily log** that can be indexed by the memory system.  
- Topic‑specific files (e.g., `github-best-practices.md`) are also indexed and can be referenced directly.  

## 4. Memory Plugin Configuration

| Setting | Value |
|---------|-------|
| **Backend** | `builtin` (default) with optional `qmd` side‑car |
| **Sources** | `memory`, `sessions` (optional) |
| **Extra Paths** | `knowledge/playbook/` (added for playbook docs) |
| **Provider** | `local` (default) – uses OpenAI‑compatible embedding model |
| **Remote Base URL** | `https://api.openai.com` (can be overridden) |
| **Fallback Provider** | `openai` (default) |
| **Vector Index** | Enabled via `sqlite-vec` extension (path: `~/.openclaw/memory/<agentId>.sqlite`) |
| **Chunking** | Tokens: 1000, Overlap: 200 |
| **Sync Triggers** | `onSessionStart`, `onSearch`, `watch` (chokidar) |
| **Cache** | Enabled, maxEntries: 5000 |

## 5. Operations

| Command | Description |
|---------|-------------|
| `openclaw memory search "keyword"` | Vector‑search the index and return top results. |
| `openclaw memory add /path/to/file.md` | Manually add a markdown file to the index. |
| `openclaw memory prune` | Remove stale entries (older than 30 days) – configurable via `memory.prune.interval`. |
| `openclaw memory export` | Export the full index to a JSON snapshot (`memory-export.json`). |

## 6. Best Practices

1. **Keep `MEMORY.md` Updated** – It serves as the primary quick‑lookup; ensure new insights are appended promptly.  
2. **Use Topic Files** – Store related knowledge in separate markdown files (e.g., `github-best-practices.md`) and reference them in the index.  
3. **Review Auto‑Captures** – Occasionally scan the `knowledge/` directory for missed entries; add any that should be persisted.  
4. **Backup** – Periodically copy the `memory/` directory to a secure backup location (`/home/legion/.openclaw/backups/memory/`).  

---  

*This playbook entry should be referenced whenever you modify the memory layout, add new knowledge files, or need to perform memory‑related maintenance tasks.* 