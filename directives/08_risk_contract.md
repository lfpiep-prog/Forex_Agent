# 08 Risk Contract

**Objective**: Ensure deterministic conversion of Trading Signals into executable Order Intents, governed by strict risk limits and account constraints.

## 1. Inputs

### 1.1 Signal
Structure received from Signal Engine:
```json
{
  "symbol": "EURUSD",
  "direction": "BUY", // or "SELL"
  "strategy": "BaselineSMA",
  "timestamp": "2024-05-20T10:00:00Z",
  "strength": 1.0, // Optional confidence score
  "metadata": {}
}
```

### 1.2 Account Snapshot (Mock Source for MVP)
Current state of the trading account.
*Note: In production, this comes from the Broker API.*
```json
{
  "balance": 10000.00,
  "equity": 10000.00,
  "currency": "EUR",
  "open_positions": [], // List of active trades
  "daily_loss_current": 0.00,
  "daily_trades_count": 0
}
```

### 1.3 Risk Configuration
Static or dynamic rules loaded at runtime.
```python
RISK_CONFIG = {
    "max_daily_loss_pct": 2.0,       # Max 2% loss of equity per day
    "max_trades_per_day": 5,
    "risk_per_trade_pct": 1.0,       # Risk 1% of equity per trade
    "max_open_lots": 1.0,            # Hard cap on total exposure
    "sl_pips_default": 20,           # Default Stop Loss if not dynamic
    "tp_pips_default": 40,           # Default Take Profit
    "min_sl_pips": 5,                # Minimum allowed SL distance
    "use_trailing_stop": False
}
```

## 2. Process
The Risk Manager performs the following steps:
1.  **Kill Switch Check**: Are any global limits (Daily Loss, Max Trades) already breached? If yes -> REJECT.
2.  **Sizing Calculation**: Calculate position size based on `risk_per_trade_pct`, `sl_pips`, and account `equity`.
3.  **Order Construction**: details (SL/TP prices) and validity checks (e.g., is size > min_lot?).

## 3. Outputs: Order Intent
The actionable instruction for the Execution Engine.

```python
class OrderIntent:
    valid: bool
    symbol: str
    direction: str # BUY/SELL
    size: float
    sl_price: float
    tp_price: float
    reason: str # "OK" or rejection reason e.g. "DAILY_LIMIT_REACHED"
```

## 4. Fail-Safes
- **Zero/Negative Balance Protection**: No orders if equity <= 0.
- **Fat Finger Check**: Reject sizes > `max_single_trade_size` (implied or explicit).
- **Stale Signal**: Reject signals older than X seconds (handled by Execution but checked here if needed).
