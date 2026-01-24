# Agent Skill Protocol

## Purpose
This directive establishes a mandatory protocol for the Agent (Antigravity) to ensure that specific project "Skills" are utilized whenever applicable to a user's request. This ensures standardized work and effectively leverages the defined capabilities of the agent customization.

## Standing Order
**Trigger:** Every user prompt (Text or Audio).

**Protocol:**
1.  **Analyze**: Understand the user's core intent.
2.  **Scan**: Review the list of available skills in `.agent/skills/`.
3.  **Execute**:
    *   **Match Found**: Explicitly load (`view_file`) and follow the skill's `SKILL.md` instructions.
    *   **No Match**: Proceed with general best practices, but consider if a new skill should be created (ref: `kaizen`).

## Principles
-   **Standardization**: Always use the defined way of doing things (Skill) over ad-hoc solutions.
-   **Transparency**: Inform the user when a skill is being applied.
-   **Continuous Improvement**: If a skill is missing, suggest creating it.

## Reference
-   `kaizen`: For the philosophy of standardized work.
-   `writing-professional-docs`: Used to draft this protocol.
