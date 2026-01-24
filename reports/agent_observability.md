# Agent Observability Report

## 1. Skill Usage
Inventory of skills used for this upgrade:

| Skill Name | Purpose | Status |
| :--- | :--- | :--- |
| `systematic-debugging` | Guide for structured error handling and investigation process | Used for `log_failure` design |
| `documentation-templates` | Format for reports and documentation | Implied usage for report structure |

## 2. Status Quo Assessment
- **Existing Logs**: Were logged to `.tmp/runs/YYYY-MM-DD/log.jsonl` (JSON) and Console (Text).
- **Correlation**: No `run_id` was present, making it hard to link CSV rows to Log entries.
- **Failures**: Errors were printed or suppressed without clear "next steps".

## 3. Upgrades Implemented
### A. Structured Logs
- **Key-Value Pairs**: All logs now JSON formatted on disk.
- **Run ID**: A global `run_id` (UUID) is generated at import time and attached to every log record.

### B. Run Summary
- `PipelineLogger` now emits start/end events with duration.
- Console output shows short-ID for quick checks.

### C. Failure Summary
- New `log_failure` helper standardizes error reporting.
- Pipeline logging catches exceptions and logs them with stack traces and actionable next steps.

## 4. How to Debug (The "Fire Drill")
**Scenario**: "The bot didn't trade, but I don't know why."

1. **Check the CSV**: Open `trade_journal.csv`. Find the row with the timestamp.
2. **Get Run ID**: Copy the `run_id` from that row.
3. **Find the Log**: Go to `.tmp/runs/<creation_date>/log.jsonl`.
4. **Grep**: `grep <RunID> log.jsonl`
5. **Analyze**:
   - Look for `event_type": "FAILURE"`
   - Read `failure_summary` and `next_steps`.

## 5. Next Steps
- Consider integrating a cloud logger (e.g., CloudWatch/Stackdriver) if moving to production servers.
- Add alerts for `level="ERROR"` logs.
