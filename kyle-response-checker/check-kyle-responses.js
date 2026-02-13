#!/usr/bin/env node
/**
 * Kyle Response Checker
 * 
 * Periodically checks GitHub issues for responses from @krobinsonca.
 * When Kyle responds, spawns an agent to resume development.
 * 
 * Usage:
 *   node check-kyle-responses.js [repo]
 *   node check-kyle-responses.js --all     // Check all configured repos
 * 
 * Following GitHub CLI best practices from /skills/github/SKILL.md
 * Uses `gh issue list --mention` to find issues tagged with @krobinsonca
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const KYLE_GITHUB = 'krobinsonca';
const STATE_FILE = path.join(__dirname, '.kyle-response-state.json');

// Configured repos
const REPOS = [
  'krobinsonca/apexform',
  'krobinsonca/hamono',
  'krobinsonca/shootrebook',
  'krobinsonca/stitchai'
];

/**
 * Load previous state (last comment ID checked per repo)
 */
function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      return JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    }
  } catch (err) {
    console.error('Error loading state:', err.message);
  }
  return {};
}

/**
 * Save state
 */
function saveState(state) {
  try {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  } catch (err) {
    console.error('Error saving state:', err.message);
  }
}

/**
 * Fetch issues mentioning Kyle in a repo
 * Uses `gh issue list --mention` per GitHub skill documentation
 */
function getIssuesMentioningKyle(repo) {
  try {
    const result = execSync(
      `gh issue list --repo ${repo} --mention ${KYLE_GITHUB} --json number,title,url,updatedAt`,
      { encoding: 'utf8' }
    );
    
    return JSON.parse(result);
  } catch (err) {
    if (!err.message.includes('no such')) {
      console.error(`Error fetching issues for ${repo}:`, err.message);
    }
    return [];
  }
}

/**
 * Get comments on an issue, sorted newest first
 */
function getIssueComments(repo, issueNumber) {
  try {
    const result = execSync(
      `gh api repos/${repo}/issues/${issueNumber}/comments --paginate`,
      { encoding: 'utf8' }
    );
    
    const comments = JSON.parse(result);
    
    // Sort by created_at descending (newest first)
    return comments.sort((a, b) => 
      new Date(b.created_at) - new Date(a.created_at)
    );
  } catch (err) {
    console.error(`Error fetching comments for ${repo}#${issueNumber}:`, err.message);
    return [];
  }
}

/**
 * Check if Kyle has responded to an issue
 */
function hasKyleResponded(comments) {
  return comments.some(comment => 
    comment.user.login.toLowerCase() === KYLE_GITHUB.toLowerCase()
  );
}

/**
 * Get the latest comment from Kyle
 */
function getLatestKyleComment(comments) {
  return comments.find(c => 
    c.user.login.toLowerCase() === KYLE_GITHUB.toLowerCase()
  );
}

/**
 * Spawn an agent to resume work on an issue
 */
function spawnResumeAgent(repo, issueNumber, issueTitle, kyleComment) {
  const message = `🔔 **Kyle Responded!**\n\n` +
    `Issue #${issueNumber} in ${repo}\n` +
    `Title: "${issueTitle}"\n\n` +
    `Kyle's response:\n` +
    `"${kyleComment.body.substring(0, 500)}${kyleComment.body.length > 500 ? '...' : ''}"\n\n` +
    `Please review his response and continue development.\n` +
    `Issue: https://github.com/${repo}/issues/${issueNumber}`;
  
  console.log(`  🚀 Spawning agent to resume work...`);
  
  // Use sessions_spawn to create a new agent session
  try {
    const { sessions_spawn } = require('openclaw');
    
    sessions_spawn({
      task: message,
      model: 'minimax2.5',
      timeoutSeconds: 1800,
      label: `resume-${repo.split('/')[1]}-${issueNumber}`
    });
    
    return true;
  } catch (err) {
    console.error('  ❌ Failed to spawn agent:', err.message);
    return false;
  }
}

/**
 * Process a single repository
 */
function processRepo(repo) {
  console.log(`\n📋 Checking ${repo}...`);
  
  const state = loadState();
  const lastState = state[repo] || { lastCommentId: 0 };
  
  // Get issues mentioning Kyle
  const issues = getIssuesMentioningKyle(repo);
  
  if (issues.length === 0) {
    console.log(`  No issues mentioning @${KYLE_GITHUB}`);
    return;
  }
  
  console.log(`  Found ${issues.length} issues mentioning @${KYLE_GITHUB}`);
  
  let newResponses = 0;
  
  for (const issue of issues) {
    const comments = getIssueComments(repo, issue.number);
    const kyleComment = getLatestKyleComment(comments);
    
    if (kyleComment) {
      // Check if we've already processed this response
      if (kyleComment.id > (lastState.lastCommentId || 0)) {
        console.log(`  ✅ New response from @${KYLE_GITHUB} on #${issue.number}`);
        
        spawnResumeAgent(repo, issue.number, issue.title, kyleComment);
        newResponses++;
        
        // Update state
        state[repo] = {
          lastCommentId: kyleComment.id,
          lastResponseTime: new Date().toISOString(),
          issueNumber: issue.number,
          issueTitle: issue.title
        };
      } else {
        console.log(`  ⏭️ Already processed #${issue.number}`);
      }
    }
  }
  
  // Save updated state
  if (newResponses > 0) {
    saveState(state);
    console.log(`  📤 Triggered ${newResponses} resume agent(s)`);
  } else {
    console.log(`  ✅ No new responses`);
  }
}

/**
 * Check all repositories
 */
function checkAllRepos() {
  console.log(`\n🔍 Kyle Response Checker - ${new Date().toISOString()}`);
  console.log(`Looking for responses from @${KYLE_GITHUB}...\n`);
  
  const args = process.argv.slice(2);
  let reposToCheck = [];
  
  if (args.includes('--all')) {
    reposToCheck = REPOS;
  } else if (args.length > 0) {
    reposToCheck = args;
  } else {
    reposToCheck = REPOS;
  }
  
  reposToCheck.forEach(processRepo);
  
  console.log('\n✅ Check complete\n');
}

// Main entry point
if (require.main === module) {
  checkAllRepos();
}

module.exports = { checkAllRepos, processRepo };
