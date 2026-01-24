# Agent Execution Safety Report

**Date:** 2026-01-24
**Author:** Antigravity (Execution Engineer)
**Status:** In Progress

## 1. Skill Usage

| Skill Name | Purpose | Application |
|ry |ry |ry |
| `cc-skill-security-review` | Security gates & Secrets | Implemented double-confirmation for live trading; audited secret logging. |
| `api-patterns` | Robustness | Defining idempotency strategy and error classification (transient vs fatal). |
| `backend-dev-guidelines` | Logging & Structure | Ensuring structured logging of order intent and clean separation of concerns. |
| `clean-code` | Code Quality | Refactoring broker logic to be readable and explicit. |

## 2. Current State Analysis (Ist-Stand)

### Broker Integration
- **Implementation**: `IGBroker` class interacting with `trading_ig` library.
- **Methods**:
    - `get_balance()`: Read-only.
    - `execute_order(intent)`: Write (Order Placement).
- **Configuration**:
    - Credentials loaded from `os.environ`.
    - `IG_ACC_TYPE` determines LIVE vs DEMO.
    - **Risk**: Single point of failure. If `IG_ACC_TYPE` is "LIVE" and credentials are valid, trading happens immediately on call.

### Safety Gaps
1.  **Accidental Live Trading**: No explicit "safety switch". A simple ENV change enables real money trading.
2.  **No Idempotency**: Logic does not prevent executing the same order intent twice (e.g., on network timeout + retry).
3.  **Symbol Allowlist**: Not strictly enforced in the broker layer (relies on upstream config).

## 3. Safety Gates Implementation Plan

### Layer 1: Configuration Gates
We introduce strict requirements for LIVE trading:
- `IG_ACC_TYPE` must be `LIVE`.
- `LIVE_TRADING_ENABLED` must be `true` (explicit boolean flag).
- `IG_API_KEY` must be present.

### Layer 2: Execution Gates (The "Safety Valve")
Before any `execute_order` call proceeds to the API:
1.  **Mode Check**: Verify if we are in LIVE or DEMO. If LIVE, verify all Layer 1 gates.
2.  **Symbol Allowlist**: Verify the requested symbol is in `config.BROKER_ALLOWLIST`.
3.  **Sanity Check**: Verify size limits (Max Lots) and constraints again (Redundant Layer).

### Layer 3: Logging & Observability
- **Intent Logging**: Log "INTENT: BUY 1.0 EURUSD" *before* attempting API call.
- **Secret Masking**: Ensure no logs contain API keys or auth tokens.

## 4. Robustness & Idempotency
- **Idempotency Key**: We will generate a unique hash for each `OrderIntent`.
- **Deduplication**: The broker will track recently processed Intent IDs (in-memory or file) to prevent immediate double-execution.
- **Error Handling**:
    - **Transient** (Network / 5xx): Retry with backoff (Safe only if idempotent).
    - **Fatal** (Auth / 4xx / Logic): Immediate fail, no retry.

## 5. Next Steps
- [ ] Modify `execution/config.py` to include safety flags.
- [ ] Create `execution/safety.py` logic.
- [ ] Patch `execution/brokers/ig_broker.py` to implement the Safety Gates.
