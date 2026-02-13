# Issue Management Playbook

**Core Philosophy**: Agents act as developers. Fix bugs, test changes, create PRs. Kyle gates features/major changes/PR merges.

## 1. Issue Creation Guidelines (2026-02-09)

1. **Research / Investigate** - Reproduce the problem, gather root-cause clues, and document findings before opening an issue.
2. **Follow Repository Templates** - Use `gh issue create --template` (or the repo-specific template) to ensure proper file structure.
3. **Be Developer-Ready** - Include:
   - **Title**: Clear, concise, prefixed with a verb (e.g., "Fix", "Add", "Refactor").
   - **Description**: What, Why, How, Tests, Screenshots, Impact, Acceptance Criteria.
   - **Labels**: Assign appropriate priority, type, and component labels.
   - **Rich Formatting**: Use headings, bullet points, code fences, tables, and inline images where helpful.

## 2. Bug Fixing & Feature Development Workflow (Updated 2026-02-12)

**Agents act as developers** - fix bugs, implement features, test changes, create PRs automatically.

### Auto-Development Rules
- **Bugs & Issues**: Fix automatically, test, create PR
- **Features**: Implement solution, test, create PR
- **Trivial Fixes** (typos, syntax, obvious one-liners): Fix directly, no PR needed
- **Minor PRs** (linting, formatting, minor config): Fix, test, merge automatically

### Approval Model (Kyle as Reviewer/Merger)
- **All PRs**: Kyle reviews and merges (features, bugs, non-trivial fixes)
- **Features**: Agents implement, create PR, Kyle approves/merges
- **Major Changes**: Agents implement with clear documentation, Kyle approves/merges
- **Trivial/Minor**: Agents can merge directly without Kyle review

### Workflow
1. **Investigate** - Reproduce bug OR understand feature requirements
2. **Implement** - Write code for fix or feature
3. **Test** - Run tests, verify functionality
4. **Commit** - Descriptive commit message
5. **PR** - Create PR with description (what/why/how)
6. **Notify** - Tag Kyle for review/merge

### When to NOT Develop
- Dev Pause Protocol active (see Section 4)
- Unclear how to implement safely
- Requires architectural decision from Kyle
- Scope is too large (break into smaller PRs first)

## 4. Dev Pause Protocol

- **Instruction**: "Fully pause all dev activity. Push completed commits to PRs."
- **Status**: All dev processes killed; sub-agents notified to finalize pending PRs and halt new development.
- **Resume Trigger**: An explicit command such as "resume dev" (or similar) from Kyle.

## 5. Critical Decisions Stored

| Decision | Summary |
|----------|---------|
| **Dev Pause Protocol** | Halt all development until a manual resume command is received. |
| **Auto-Develop Policy** | Agents implement bugs/features, test, create PRs. Kyle reviews/merges PRs. Minor PRs (linting) auto-merge. |
| **Feature Development** | Agents develop solutions for feature requests and create PRs. Kyle approves/merges. |

---

*All developers should reference this playbook before opening new issues or merging changes.*\n\n## 6. Agent-Kyle Decision Loop (2026-02-12, Updated 2026-02-12)

When an agent needs architectural input or a decision from Kyle:

1. **Tag Kyle in a GitHub Issue** - Use `@krobinsonca` in the issue body or a comment
2. **Document the Question** - Be clear about what decision is needed
3. **Continue with Other Work** - Agent does NOT wait; continues productive tasks
4. **Kyle Responds in GitHub** - Kyle replies with his decision
5. **Kyle Response Checker Detects Response** - Cron job runs every 5 minutes
6. **Sub-Agent Resumes Work** - New agent spawned to continue implementation

**Key Principle**: Agents should NOT wait indefinitely. Tag Kyle, continue working, and resume when the response checker detects his answer.

### How to Tag Kyle

```bash
# In an issue comment
gh issue comment <issue-number> --body "@krobinsonca Should we use Firebase or Supabase for the Guild System backend?"

# When creating an issue
gh issue create --title "Guild System Architecture Decision" --body "@krobinsonca Need your input on backend choice"
```

### Kyle Response Checker

- **Location**: `/home/legion/.openclaw/workspace/kyle-response-checker/check-kyle-responses.js`
- **Schedule**: Every 5 minutes (cron job)
- **What it does**: Checks all repos for issues tagged with @krobinsonca where Kyle has commented since the last check
- **Action**: Spawns sub-agents to resume work on issues with new responses