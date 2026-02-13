#!/usr/bin/env node
/**
 * GitHub Webhook Bridge
 * 
 * Listens for GitHub webhook events and:
 * 1. Notifies Kyle when tagged in issues via Telegram
 * 2. Triggers agent resume when Kyle responds
 * 
 * Usage:
 *   node server.js [port]
 *   
 * Environment:
 *   TELEGRAM_BOT_TOKEN - Telegram bot token (optional, reads from openclaw.json)
 *   TELEGRAM_CHAT_ID - Telegram chat ID (optional, reads from openclaw.json)
 */

const express = require('express');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.argv[2] || 3000;

// Load Telegram config from openclaw.json
function loadTelegramConfig() {
  try {
    const configPath = '/home/legion/.openclaw/openclaw.json';
    if (fs.existsSync(configPath)) {
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      
      // Try main account first
      const mainAccount = config?.channels?.telegram?.accounts?.main;
      if (mainAccount?.botToken) {
        return {
          botToken: mainAccount.botToken,
          chatId: '7162874831' // Kyle's Telegram ID
        };
      }
      
      // Fallback to environment
      return {
        botToken: process.env.TELEGRAM_BOT_TOKEN || '',
        chatId: process.env.TELEGRAM_CHAT_ID || ''
      };
    }
  } catch (err) {
    console.error('Error loading openclaw config:', err.message);
  }
  return {
    botToken: process.env.TELEGRAM_BOT_TOKEN || '',
    chatId: process.env.TELEGRAM_CHAT_ID || ''
  };
}

const TELEGRAM_CONFIG = loadTelegramConfig();

// Configuration
const CONFIG = {
  // Kyle's identifiers
  KYLE_GITHUB: 'krobinsonca',
  KYLE_TELEGRAM: '7162874831',
  
  // Webhook secrets per repo
  webhookSecrets: {
    'krobinsonca/apexform': process.env.WEBHOOK_SECRET_APEXFORM || '',
    'krobinsonca/hamono': process.env.WEBHOOK_SECRET_HAMONO || '',
    'krobinsonca/shootrebook': process.env.WEBHOOK_SECRET_SHOOTREBOOK || '',
    'krobinsonca/stitchai': process.env.WEBHOOK_SECRET_STITCHAI || '',
  },
  
  // Legacy single secret (fallback)
  webhookSecret: process.env.WEBHOOK_SECRET || '',
  
  // Notification targets
  telegramBotToken: TELEGRAM_CONFIG.botToken,
  telegramChatId: TELEGRAM_CONFIG.chatId,
};

// Middleware to parse JSON
app.use(express.json({
  verify: (req, res, buf) => {
    req.rawBody = buf;
  }
}));

/**
 * Get webhook secret for a repository
 */
function getRepoSecret(repoFullName) {
  return CONFIG.webhookSecrets[repoFullName] || CONFIG.webhookSecret;
}

/**
 * Verify GitHub webhook signature
 */
function verifySignature(req, repoFullName) {
  const secret = getRepoSecret(repoFullName);
  if (!secret) return true;
  
  const signature = req.headers['x-hub-signature-256'];
  if (!signature) return false;
  
  const hmac = crypto.createHmac('sha256', secret);
  const digest = 'sha256=' + hmac.update(req.rawBody).digest('hex');
  
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(digest));
}

/**
 * Send notification to Telegram
 */
async function sendTelegramNotification(message) {
  if (!CONFIG.telegramBotToken || !CONFIG.telegramChatId) {
    console.log('Telegram not configured - skipping notification');
    return;
  }
  
  const url = `https://api.telegram.org/bot${CONFIG.telegramBotToken}/sendMessage`;
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: CONFIG.telegramChatId,
        text: message,
        parse_mode: 'Markdown'
      })
    });
    
    if (!response.ok) {
      const error = await response.text();
      console.error('Telegram API error:', response.status, error);
    } else {
      console.log('Telegram notification sent successfully');
    }
  } catch (err) {
    console.error('Telegram notification failed:', err.message);
  }
}

/**
 * Notify Kyle when tagged
 */
async function notifyKyle(issue, actor) {
  const message = `🔔 *Agent Needs Your Input*\n\n` +
    `Issue #${issue.number}: ${issue.title}\n` +
    `Repo: ${issue.repository.full_name}\n` +
    `Tagged by: @${actor}\n\n` +
    `[View Issue](${issue.html_url})`;
  
  console.log('Notifying Kyle about:', issue.title);
  await sendTelegramNotification(message);
}

/**
 * Trigger agent resume when Kyle responds
 */
async function triggerAgentResume(issue, comment) {
  const issueNumber = issue.number;
  const repoFullName = issue.repository.full_name;
  
  const isKyle = comment.user.login.toLowerCase() === CONFIG.KYLE_GITHUB.toLowerCase();
  if (!isKyle) {
    console.log(`Comment by ${comment.user.login}, not triggering resume`);
    return;
  }
  
  console.log(`Kyle responded to issue #${issueNumber}, triggering agent resume...`);
  
  await sendTelegramNotification(`✅ *Agent Resume Triggered*\n\n` +
    `Kyle responded to issue #${issueNumber} in ${repoFullName}\n` +
    `Agent will resume work.`);
}

/**
 * Handle GitHub issue comment events
 */
async function handleIssueComment(event) {
  const { issue, comment, action, repository } = event;
  
  if (action !== 'created') return;
  
  const body = (comment.body + ' ' + (issue.body || '')).toLowerCase();
  const mentionsKyle = body.includes(`@${CONFIG.KYLE_GITHUB.toLowerCase()}`);
  
  if (mentionsKyle) {
    await notifyKyle({
      number: issue.number,
      title: issue.title,
      html_url: issue.html_url,
      repository: { full_name: repository.full_name }
    }, comment.user.login);
  } else {
    await triggerAgentResume({
      number: issue.number,
      title: issue.title,
      html_url: issue.html_url,
      repository: { full_name: repository.full_name }
    }, comment);
  }
}

/**
 * Handle GitHub issue events
 */
async function handleIssues(event) {
  const { issue, action, repository } = event;
  
  if (action === 'opened') {
    const body = (issue.body || '').toLowerCase();
    const mentionsKyle = body.includes(`@${CONFIG.KYLE_GITHUB.toLowerCase()}`);
    
    if (mentionsKyle) {
      await notifyKyle({
        number: issue.number,
        title: issue.title,
        html_url: issue.html_url,
        repository: { full_name: repository.full_name }
      }, issue.user.login);
    }
  }
}

// Webhook endpoint
app.post('/webhook', async (req, res) => {
  const event = req.headers['x-github-event'];
  const repoFullName = req.body?.repository?.full_name || '';
  
  if (!verifySignature(req, repoFullName)) {
    console.warn('Invalid webhook signature for', repoFullName);
    return res.status(401).send('Invalid signature');
  }
  
  console.log(`GitHub event: ${event} from ${repoFullName}`);
  
  try {
    switch (event) {
      case 'issue_comment':
        await handleIssueComment(req.body);
        break;
      case 'issues':
        await handleIssues(req.body);
        break;
      default:
        console.log(`Ignoring event: ${event}`);
    }
    
    res.status(200).send('OK');
  } catch (err) {
    console.error('Webhook error:', err);
    res.status(500).send('Error');
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    telegram: CONFIG.telegramBotToken ? 'configured' : 'not configured'
  });
});

app.listen(PORT, () => {
  console.log(`Webhook bridge running on http://localhost:${PORT}`);
  console.log(`Telegram: ${CONFIG.telegramBotToken ? 'configured' : 'NOT CONFIGURED'}`);
});

if (require.main === module) {
  process.on('SIGTERM', () => {
    console.log('Shutting down...');
    process.exit(0);
  });
}
