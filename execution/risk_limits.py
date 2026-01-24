from dataclasses import dataclass
from typing import List, Dict

@dataclass
class RiskConfig:
    max_daily_loss_pct: float = 2.0
    max_trades_per_day: int = 5
    risk_per_trade_pct: float = 1.0
    max_open_lots: float = 1.0
    sl_pips_default: float = 20.0
    tp_pips_default: float = 40.0
    min_sl_pips: float = 5.0
    use_trailing_stop: bool = False

def check_daily_limits(account_snapshot: Dict, config: RiskConfig) -> Dict:
    """
    Checks if account is within daily risk limits.
    Returns: {"allowed": bool, "reason": str}
    """
    
    # 1. Daily Loss Limit
    # Assuming account_snapshot has 'daily_loss_current' as a positive float for loss amount
    # or negative for profit. We care about LOSS.
    # Let's assume daily_loss_current is POSITIVE when losing money.
    
    current_loss = account_snapshot.get("daily_loss_current", 0.0)
    equality = account_snapshot.get("equity", 1000.0) # avoid div by zero if missing
    
    if equality <= 0:
         return {"allowed": False, "reason": "EQUITY_ZERO_OR_NEGATIVE"}

    loss_pct = (current_loss / equality) * 100.0
    
    if loss_pct >= config.max_daily_loss_pct:
        return {
            "allowed": False, 
            "reason": f"DAILY_LOSS_LIMIT_REACHED: {loss_pct:.2f}% >= {config.max_daily_loss_pct}%"
        }

    # 2. Daily Trades Count
    daily_trades = account_snapshot.get("daily_trades_count", 0)
    if daily_trades >= config.max_trades_per_day:
        return {
            "allowed": False,
            "reason": f"MAX_TRADES_LIMIT_REACHED: {daily_trades} >= {config.max_trades_per_day}"
        }

    return {"allowed": True, "reason": "OK"}

def check_exposure_limits(account_snapshot: Dict, new_size_lots: float, config: RiskConfig) -> Dict:
    """
    Checks if adding new trade size would breach max exposure limits.
    """
    current_open_lots = 0.0
    for trade in account_snapshot.get("open_positions", []):
        current_open_lots += trade.get("size", 0.0)
        
    projected_lots = current_open_lots + new_size_lots
    
    if projected_lots > config.max_open_lots:
         return {
            "allowed": False, 
            "reason": f"MAX_EXPOSURE_LIMIT: {projected_lots:.2f} > {config.max_open_lots}"
        }
        
    return {"allowed": True, "reason": "OK"}
