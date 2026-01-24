---
name: managing-project-tasks
description: Organizes project tasks and manages TODOs efficiently. Use when the user asks to plan a project, track progress, or create a roadmap.
---

# Project Task Management

## When to use this skill
- User says "What should I do next?"
- User wants to create a `task.md` or `TODO` list.
- User feels overwhelmed and needs structure.

## Workflow
- [ ] **Inventory**: Scan the workspace for existing TODOs (`grep_search` "TODO").
- [ ] **Prioritize**: Rank tasks by Impact vs. Effort.
- [ ] **Structure**: Create or Update `task.md`.
- [ ] **Break Down**: Decompose large items into sub-tasks (atomic units of work).
- [ ] **Review**: Present the plan to the user for confirmation.

## Instructions
1.  **Single Source of Truth**: Maintain ONE main task list (usually `task.md` or `plan.md`).
2.  **Status Tracking**:
    -   `[ ]` Pending
    -   `[/]` In Progress
    -   `[x]` Done
3.  **Atomic Tasks**: A task should be finishable in one session (< 1 hour).
    -   *Bad*: "Build the App"
    -   *Good*: "Create login form component"
4.  **Context**: Link tasks to specific files or lines of code.

## Resources
- `task_boundary` tool: Use this to track the *active* task in the agent session.
