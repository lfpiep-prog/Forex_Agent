---
name: debugging-code-systematically
description: Debugs code using a hypothesis-driven approach. Use when the user reports a bug, error, or unexpected behavior.
---

# Systematic Code Debugging

## When to use this skill
- A test fails, and the cause is unknown.
- The user reports a runtime error or exception.
- The application hangs or crashes.
- Unexpected output is observed.

## Workflow
- [ ] **Analyze**: Read the error message, stack trace, and relevant logs.
- [ ] **Reproduce**: Create a minimal reproduction script or identifying the specific input that causes failure.
- [ ] **Hypothesize**: Formulate a specific hypothesis about *why* it fails.
- [ ] **Validate**: Add logging or run the reproduction script to confirm the hypothesis.
- [ ] **Fix**: Implement the fix.
- [ ] **Verify**: Run the reproduction script again to ensure it passes.

## Instructions
1.  **Do not guess.** Start by observing.
2.  If the error is in a browser/UI, check the browser console logs first.
3.  If the error is in a terminal command, check the `command_status`.
4.  **Create a reproduction case.** If you cannot reproduce it, you cannot reliably fix it.
    -   Create a file `reproduce_issue.py` (or similar).
    -   Make it fail with the current code.
5.  **Scientific Method**:
    -   *Hypothesis*: "The variable `x` is None because the API returned 404."
    -   *Test*: "I will print `x` before line 10."
6.  **Apply Fix**: Only AFTER the hypothesis is validated.

## Resources
- Use `grep_search` to find error strings in the codebase.
- Use `view_file` to examine the context of the stack trace.
