#!/usr/bin/env node
/**
 * Agent Decision Request Script
 * 
 * Used by agents to tag Kyle in GitHub issues when they need input.
 * This will trigger webhook notifications and help track pending decisions.
 * 
 * Usage:
 *   node tag-kyle.js --repo owner/repo --issue 123 "Your question here"
 *   node tag-kyle.js --repo owner/repo --create --title "Feature Question" --body "..."
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const KYLE_TAG = '@Scorpion23ca';
const WEBHOOK_BRIDGE_URL = process.env.WEBHOOK_BRIDGE_URL || 'http://localhost:3000';

/**
 * Get GitHub token from environment
 */
function getGitHubToken() {
  return process.env.GITHUB_TOKEN || 
         execSync('gh auth token', { encoding: 'utf8' }).trim();
}

/**
 * Tag Kyle in an existing issue
 */
function tagKyleInIssue(repo, issueNumber, question) {
  const token = getGitHubToken();
  
  // Add comment tagging Kyle
  const comment = `${KYLE_TAG} \n\n${question}`;
  
  const result = execSync(
    `gh api repos/${repo}/issues/${issueNumber}/comments \
      --header "Authorization: Bearer ${token}" \
      --method POST \
      --field body="${comment.replace(/"/g, '\\"')}"`,
    { encoding: 'utf8' }
  );
  
  const commentData = JSON.parse(result);
  console.log(`✅ Tagged Kyle in issue #${issueNumber}`);
  console.log(`   Comment: ${commentData.html_url}`);
  
  return commentData;
}

/**
 * Create a new issue tagging Kyle
 */
function createIssueTaggingKyle(repo, title, body) {
  const token = getGitHubToken();
  
  // Add Kyle tag to body
  const fullBody = `${KYLE_TAG}\n\n${body}`;
  
  const result = execSync(
    `gh api repos/${repo}/issues \
      --header "Authorization: Bearer ${token}" \
      --method POST \
      --field title="${title.replace(/"/g, '\\"')}" \
      --field body="${fullBody.replace(/"/g, '\\"')}"`,
    { encoding: 'utf8' }
  );
  
  const issueData = JSON.parse(result);
  console.log(`✅ Created issue #${issueData.number} and tagged Kyle`);
  console.log(`   Issue: ${issueData.html_url}`);
  
  return issueData;
}

/**
 * Check if issue is in pending state (Kyle hasn't responded yet)
 */
function isIssuePending(repo, issueNumber) {
  try {
    const token = getGitHubToken();
    const result = execSync(
      `gh api repos/${repo}/issues/${issueNumber}/events \
        --header "Authorization: Bearer ${token}"`,
      { encoding: 'utf8' }
    );
    
    const events = JSON.parse(result);
    // Check if Kyle has commented since the tag
    const lastKyleComment = events.find(e => 
      e.event === 'commented' && 
      e.actor.login === 'Scorpion23ca'
    );
    
    return !lastKyleComment;
  } catch (err) {
    return true; // Assume pending if we can't check
  }
}

// CLI interface
const args = process.argv.slice(2);
const repoArg = args.find(a => a.startsWith('--repo='))?.split('=')[1];
const issueArg = args.find(a => a.startsWith('--issue='))?.split('=')[1];
const createArg = args.includes('--create');
const titleArg = args.find(a => a.startsWith('--title='))?.split('=')[1]?.replace(/_/g, ' ');
const bodyArg = args.find(a => a.startsWith('--body='))?.split('=')[1]?.replace(/_/g, ' ');

if (!repoArg) {
  console.log(`
Agent Decision Request Script

Usage:
  node tag-kyle.js --repo owner/repo --issue 123 "Your question here"
  node tag-kyle.js --repo owner/repo --create --title "Issue Title" --body "Description..."

Options:
  --repo=owner/repo    Repository (required)
  --issue=number       Existing issue number (for commenting)
  --create             Create a new issue
  --title="..."        Issue title (for --create)
  --body="..."         Issue body (for --create)

Environment:
  GITHUB_TOKEN         GitHub API token (or use 'gh auth token')
  WEBHOOK_BRIDGE_URL   Webhook bridge URL (default: http://localhost:3000)

Example:
  node tag-kyle.js --repo krobinsonca/hamono --issue 23 \\
    "Should we use Firebase or Supabase for the Guild System backend?"
  `);
  process.exit(1);
}

// Get the question from remaining args
const question = args.filter(a => !a.startsWith('--'))
  .join(' ')
  .trim();

if (createArg) {
  if (!titleArg) {
    console.error('Error: --title required with --create');
    process.exit(1);
  }
  createIssueTaggingKyle(repoArg, titleArg, bodyArg || question);
} else if (issueArg) {
  if (!question) {
    console.error('Error: Question text required');
    process.exit(1);
  }
  tagKyleInIssue(repoArg, parseInt(issueArg), question);
} else {
  console.error('Error: --issue or --create required');
  process.exit(1);
}
