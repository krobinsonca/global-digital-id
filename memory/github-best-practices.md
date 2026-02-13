# GitHub Best Practices (Updated 2026-02-12)

## Issue Management
- **Referencing Issues**: Use `#<issue-number>` for cross‑references; include the repository name when the context is ambiguous.
- **Issue Titles**: Clear, concise, and prefixed with a verb (e.g., “Add”, “Fix”, “Refactor”). Include a ticket/issue number if it helps locate the work.
- **Labels**: Maintain a lean set of standardized labels for priority, type, and component. Keep the label list documented and avoid proliferating rarely‑used tags.
- **Checklists**: Include a short checklist in every issue body to capture required information (steps to reproduce, expected outcome, environment, screenshots, etc.).
- **Automation**: Use GitHub Actions to auto‑label, comment, or close issues that stagnate (e.g., no updates for 7 days).

## Issue Templates
- Create templates for **Bug Reports**, **Feature Requests**, and **Questions** in `.github/ISSUE_TEMPLATE/`.
- Use YAML front‑matter for structured fields (e.g., `contact`, `what-happened`, `environment`). Link to external documentation for reporters.
- Example template fields:
  ```yaml
  contact: ex@example.com
  what-happened: |
    Briefly describe the problem.
  environment: |
    OS, browser, software version
  ```

## Workflow Automation
- **Auto‑Close Incomplete Issues**: After 7 days of no activity, comment with a reminder; after 14 days, close with the “incomplete” label.
- **Prompt for Missing Details**: If required fields are empty, automatically comment asking for the missing information.
- **Auto‑Label**: Use Actions to assign labels based on keywords in the title or body.
- **Branching Conventions**: Follow `feature/<short‑desc>`, `bugfix/<issue‑number>`, `hotfix/<short‑desc>`.

## Issue Lifecycle
1. **Open** – All required fields filled, linked to supporting docs or screenshots.
2. **In Progress** – Assign an owner, link to a PR, update the status.
3. **Closed** – Ensure the merge is clean, update the changelog, reference the issue in the commit message.

## Issue Cleanup
- Periodically triage open issues: label as `status/pending`, `status/deferred`, or `status/duplicate`.
- Consolidate duplicates and reference the original issue.
- Use `needs-more-info` for issues lacking details; request clarification before proceeding.

## Research & Feature Proposals
- Open a `feature` issue with a descriptive title and sections for **Motivation**, **Proposed Solution**, and **Impact**.
- Reference related issues, research notes, or design docs.
- Tag relevant team members for feedback.

## Agent Integration
Agents can automatically:
- Scan new issues for keywords and suggest appropriate labels.
- Comment with standardized prompts (e.g., “Thanks for the issue! Please provide more details on …”).
- Trigger GitHub Actions that lint issue bodies for formatting compliance.
- Generate follow‑up tasks or subtasks in linked project boards.

## Markdown Formatting
- Use **bold** for emphasis, `code` for inline snippets, and > blockquotes for important notes.
- Keep bullet lists shallow; avoid deep nesting.
- Fence code blocks with triple backticks and specify the language when possible.

## Example Issue Body

```markdown
## Title
Fix typo in README introduction

## Description
A small typo (“recieve” instead of “receive”) appeared in the README intro paragraph.

## Steps to Reproduce
1. Open README.md
2. Look at the first paragraph

## Expected Result
The typo should be corrected to “receive”.

## Actual Result
The typo remains unchanged.

## Checklist
- [x] I have searched for similar issues
- [x] I have reproduced the issue
- [ ] I have added a label (bug)

## Additional Information
Suggested commit message: “Fix typo in README intro”
```

--- 

Updated to reflect current best‑practice workflows and to give agents clear guidance for issue‑management automation.