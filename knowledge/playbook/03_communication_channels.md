# Communication Channels – Operations Playbook

## 1. Telegram

- **Status**: Disabled (`enabled: false`) – cannot send messages due to privacy‑policy restrictions on bot‑initiated outreach.  
- **Outbound Capability**: Confirmed that messages **can** be sent from the bot to users, but inbound messages from users to the bot are blocked by Telegram’s privacy settings.  
- **Work‑around**: Use WhatsApp or Tailscale/WebChat for proactive outreach.

## 2. WhatsApp

- **QR‑Code Login** – Open the Tailscale webchat (or the WhatsApp app) and scan the QR code displayed at `http://legion-y540-15irh.taild545b5.ts.net:18789`.  
- **Linking Steps** – In the WhatsApp mobile app:  
  1. Open **Linked Devices** → **Link a Device**.  
  2. Scan the QR code shown on the webchat page.  
  3. After linking, the device will show “hi” as a test message and can receive replies.  
- **Current State** – Ready for use; can send and receive messages once the QR code is scanned and the device is linked.

## 3. Tailscale WebChat (Phone‑Fallback)

- **Access URL** – `http://legion-y540-15irh.taild545b5.ts.net:18789` (or the short alias `https://tg.legion.local`).  
- **How to Use** –  
  1. Ensure your phone is connected to the Tailscale network (VPN on).  
  2. Open the URL in any mobile browser.  
  3. The webchat will greet you with “hi” and allow you to type messages.  
- **Advantages** – No app install required; works on any device with Tailscale connectivity; reliable for proactive messaging.

## 4. Email (Microsoft Graph API)

- **Access Method** – `node email.js` utility (`check`, `refresh`, `send`).  
- **Account Coverage** – Both `kyle.robinson@briartech.ca` and `info@kylerobinsonphotography.com` are covered.  
- **Authentication** – Uses OAuth token stored in `~/.openclaw/email-config.json`; token refreshes automatically (`node email.js refresh`).  
- **Test Message** – Recent test email was sent to `kyle@briartech.ca` with subject “Tailscale Dashboard”. Check inbox or spam for delivery.  

## 5. Other Channels (Status Summary)

| Channel | Enabled? | Primary Use | Notes |
|---------|----------|-------------|-------|
| Telegram | ❌ | — | Blocked inbound; outbound possible but not reliable for proactive outreach. |
| WhatsApp | ✅ | Proactive, bidirectional messaging | QR‑code linking required; currently the primary proactive channel. |
| Tailscale WebChat | ✅ | Proactive, browser‑based | Works on any device with Tailscale VPN; recommended fallback. |
| Email (Graph) | ✅ | Notifications, non‑urgent updates | Token refreshes automatically; test emails successful. |
| Signal / iMessage / Slack / Discord | — | — | Not currently configured. |

**Quick Reference** – To open the WhatsApp or Tailscale webchat, click the respective link or scan the QR code provided by the `openclaw` dashboard. 

---  

*Use this playbook entry as a cheat‑sheet when configuring new channels or troubleshooting existing ones.* 