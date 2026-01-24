# 01 Minimal Rules

1. **No Secrets**: Never commit API keys or credentials. Use `.env`.
2. **Script Everything**: Any repeatable action must be a script in `execution/`.
3. **Ask First**: The Agent must explicitly ask for missing information or clarifications.
4. **Flag Assumptions**: Mark any non-trivial decision as an **Assumption** to be verified later.
5. **Keep it Simple**: Do not add unnecessary complexity or rules early on.

6. **Traceability**: All automatic execution cycles must produce structured logs (JSON) and an entry in a trade journal.
7. **Validation First**: Before live execution, every component must have a "Dry Run" mode or mock stub.
