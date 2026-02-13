# API Configuration – Operations Playbook

## 1. Moonshot (Kimi‑K2.5)

- **Provider**: `moonshot`  
- **Base URL**: `https://api.moonshot.ai/v1`  
- **Model ID**: `kimi-k2.5` (262 K context)  
- **API Key** (provided by Kyle): `sk-PTCuHxxpfoZmF6Qo3kFuOx0q80dbyEAk85HHFZ2QR1BACiwa`  
- **Configuration Location** – `/home/legion/.openclaw/openclaw.json` → `models.providers.moonshot` block.  
- **Verification** – Direct API test passed; OpenClaw status shows `default kimi-k2.5 (262k ctx)`.

## 2. MiniMax (minimax‑m2.1)

- **Alias**: `minimax`  
- **Provider**: `openrouter` (via `openrouter/minimax/minimax-m2.1`)  
- **Cost**: $0.001 per 1 K tokens; 300 prompts per 5 hours (paid plan).  
- **Use Cases**: Reserved for critical coding / heavy‑reasoning tasks.  

## 3. OpenRouter (Auto / Auto‑selected)

- **Default Provider** for most free‑tier models.  
- **Key Mappings** (excerpt from `openclaw.json`):
  ```json
  "providers": {
    "openrouter/auto": { "alias": "OpenRouter" },
    "openrouter/nvidia/nemotron-3-nano-30b-a3b:free": { "alias": "nemotron" },
    "openrouter/z-ai/glm-5": { "alias": "glm5" }
  }
  ```
- **API Keys** – Stored in the same `openclaw.json` under `auth` → `profiles.openrouter:default`.  

## 4. Brave Search (Web Search)

- **API Key** – `BSABBBsw_DQ3PRYx5Lb94cFk1HsBpLk` (stored in `tools.web.search.apiKey`).  
- **Endpoint** – `https://api.brave.com` (via OpenRouter proxy).  
- **Default Query Limits** – Up to 10 results per request; 5 s timeout.  
- **Usage** – `openclaw web_search "query string"`.

## 5. Microsoft Graph API (Email)

- **Accounts** – `kyle.robinson@briartech.ca`, `info@kylerobinsonphotography.com`.  
- **Token Management** – `node email.js refresh` renews token (≈1 hour lifetime).  
- **Key File** – `~/.openclaw/email-config.json`.  
- **Scope** – Full mailbox access; test email sent to `kyle@briartech.ca`.  

## 6. OpenAI Compatible (Fallback / Legacy)

- **OpenAI API Key** – `sk-proj-...T54A` (patched into `plugins.memory-lancedb.config.embedding.apiKey`).  
- **Model** – Used for embedding generation in the `memory-lancedb` plugin.  
- **Endpoint** – OpenAI completion endpoint (used indirectly via the plugin).  

## 7. Other Service Credentials (Stored in `openclaw.json`)

| Service | Key / Secret | Location in JSON |
|---------|--------------|-------------------|
| NVIDIA (CUDA / Developer) | `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` | `auth.profiles.openrouter:nvidia` |
| MiniMax Portal Auth | (empty for now) | — |
| OpenRouter Free Tier | `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` | `auth.profiles.openrouter:default` |

**Note** – All API credentials are **sensitive**; do not share publicly. Use `openclaw doctor --non-interactive` to verify that each provider loads correctly after any change.

---  

*Refer to the individual config files (`openclaw.json`, `email-config.json`) for the most up‑to‑date values.* 