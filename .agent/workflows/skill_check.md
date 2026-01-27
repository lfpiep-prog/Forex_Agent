---
description: Protocol for checking and applying skills before task execution
---

# Skill Check Workflow

**Trigger:** Run this workflow at the start of EVERY user request.

## Steps

1.  **Scan Skills Directory**
    - List/Recall available skills in `.agent/skills`.

2.  **Analyze Context**
    - Review `task.md` (current active task).
    - Review User Request (latest prompt).
    - Review File Context (open files).

3.  **Select Candidates**
    - Match keywords and intent to Skill Descriptions.
    - *Example:* "Debug" -> `systematic-debugging`
    - *Example:* "Improve/Refactor" -> `kaizen`
    - *Example:* "Plan" -> `concise-planning`, `writing-plans`
    - *Example:* "Test" -> `testing-patterns`

4.  **Activate Skills**
    - Use `view_file` to read the `SKILL.md` of selected skills.
    - **CRITICAL**: If a skill is selected, you MUST follow its instructions EXACTLY.

5.  **Report**
    - In the final response to the user, include a section:
      > **Active Skills:** [List of skills used]
      > *Reasoning:* [Short explanation]

## Current Skill Map (Dynamic)

- `analyzing-market-data`: OHLCV, trends, signals.
- `api-patterns`: API design, REST/GraphQL.
- `architecture`: Major design decisions, trade-offs.
- `backend-dev-guidelines`: Node/Express, architecture layers.
- `clean-code`: Code quality, simplicity.
- `code-review-checklist`: Reviewing code.
- `concise-planning`: creating atomic checklists.
- `creating-skills`: Creating new skill folders.
- `debugging-code-systematically`: Bug investigation protocol.
- `designing-modern-ui`: UI/UX, Tailwind, React.
- `file-organizer`: File management/cleanup.
- `forex-strategy-creator`: 1H candle strategies.
- `forex-strategy-optimizer`: Optimizing strategies.
- `git-pushing`: Committing/pushing changes.
- `kaizen`: Continuous improvement, refactoring.
- `managing-project-tasks`: Task tracking (task.md).
- `planning-with-files`: Complex task planning.
- `product-manager-toolkit`: Requirements, prioritization.
- `prompt-engineering`: Improving prompts.
- `python-patterns`: Python specific patterns.
- `react-best-practices`: Front-end performance.
- `senior-architect`: High-level system design.
- `software-architecture`: General architecture.
- `systematic-debugging`: (Same as debugging-code-systematically? Check duplicates).
- `testing-patterns`: Unit testing, TDD.
- `writing-plans`: Implementation specs.
- `writing-professional-docs`: Documentation.
