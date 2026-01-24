# Execution Contract

This document defines the interface for the Execution Layer.

## 1. Concepts

- **OrderIntent**: A structured request to place an order. It is the "source of truth" for what the strategy wants to do.
- **OrderResult**: The outcome of an execution attempt.
- **Idempotency**: Every `OrderIntent` must have a unique ID (`idempotency_key`). The execution layer must ensure that submitting the same key multiple times does NOT result in duplicate orders.

## 2. Data Structures

### OrderIntent

| Field | Type | Description |
| :--- | :--- | :--- |
| `idempotency_key` | `str` (UUID) | Unique identifier for this request. |
| `symbol` | `str` | e.g., "EUR_USD". |
| `direction` | `str` | "BUY" or "SELL". |
| `quantity` | `int` | Number of units (e.g., 10000). |
| `order_type` | `str` | "MARKET" or "LIMIT". |
| `limit_price` | `float` (Optional) | Required if order_type is LIMIT. |
| `created_at` | `datetime` | UTC timestamp when intent was generated. |

### OrderResult

| Field | Type | Description |
| :--- | :--- | :--- |
| `status` | `str` | "ACCEPTED", "FILLED", "REJECTED", "FAILED". |
| `broker_order_id` | `str` (Optional) | ID returned by the broker. |
| `filled_price` | `float` (Optional) | Average fill price if filled. |
| `filled_quantity` | `int` | Amount filled. |
| `timestamp` | `datetime` | UTC timestamp of the result. |
| `error_message` | `str` (Optional) | Details if failed/rejected. |
| `raw_response` | `dict` (Optional) | debugging info from broker. |

## 3. Workflow

1.  **Strategy** generates a signal (e.g., "BUY EUR_USD").
2.  **Risk Layer** validates/sizes the order -> outputs `OrderIntent`.
3.  **Execution Router** receives `OrderIntent`.
    *   Checks `idempotency_key` (have we seen this?).
    *   If fresh:
        *   Determines destination (Mock vs. Real).
        *   Calls `broker.execute(intent)`.
    *   If seen:
        *   Returns previous `OrderResult`.
4.  **Broker** returns `OrderResult`.
5.  **Router** logs the event and returns `OrderResult` to caller.

## 4. Error Handling & Retry Policy

- **Network Errors**: Retry with exponential backoff (up to 3 times).
- **Logic Errors** (e.g., "Insufficient Funds", "Invalid Symbol"): Do NOT retry. Fail fast.
- **Unknown States**: If a request times out but we don't know if it hit the exchange, fetch order status by `idempotency_key` or `client_order_id`.
