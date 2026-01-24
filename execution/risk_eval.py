from typing import Dict, Optional
from dataclasses import dataclass, asdict
from execution.risk_limits import RiskConfig, check_daily_limits, check_exposure_limits

@dataclass
class OrderIntent:
    valid: bool
    symbol: str
    direction: str
    size: float
    sl_price: float
    tp_price: float
    reason: str

    def to_dict(self):
        return asdict(self)

def calculate_position_size(equity: float, risk_pct: float, sl_pips: float, pip_value_per_lot: float = 10.0) -> float:
    """
    Calculate position size in lots based on risk amount and SL distance.
    Formula: RiskAmount / (SL_pips * PipValue)
    Simplification: Assuming standard lot ($10/pip) for EURUSD approx. 
    In prod, pip_value depends on pair.
    """
    if sl_pips <= 0:
        return 0.0
        
    risk_amount = equity * (risk_pct / 100.0)
    # limit risk amount to equity just in case
    risk_amount = min(risk_amount, equity)
    
    # Cost per lot for this SL distance
    cost_per_lot = sl_pips * pip_value_per_lot
    
    if cost_per_lot == 0:
        return 0.0
        
    size = risk_amount / cost_per_lot
    # Round to 2 decimals (mini lots) - Broker specific
    return round(size, 2)

def evaluate_risk(signal: Dict, account_snapshot: Dict, config: RiskConfig) -> OrderIntent:
    """
    Main entry point to convert a Signal into an OrderIntent.
    """
    symbol = signal.get("symbol", "UNKNOWN")
    direction = signal.get("direction", "BUY")
    
    # 1. Global Kill Switch / Daily Limits
    limit_check = check_daily_limits(account_snapshot, config)
    if not limit_check["allowed"]:
        return OrderIntent(
            valid=False, symbol=symbol, direction=direction, 
            size=0.0, sl_price=0.0, tp_price=0.0, 
            reason=limit_check["reason"]
        )

    # 2. Determine SL/TP
    # If strategy provides SL/TP, use them? Or override?
    # For MVP, let's use config defaults if not in signal (Signal might ideally have them)
    # But current Signal contract doesn't explicitly guarantee SL/TP prices.
    # Let's assume we use fixed pips from config for MVP.
    
    # Approximate current price needed to calc SL/TP levels.
    # Signal MIGHT have 'price'. If not, we can't set SL/TP prices without market data.
    # MVP HACK: If signal doesn't have price, we assume it's a MARKET order intent 
    # and we specify SL/TP in PIPS relative to fill price later? 
    # OR we need current price here.
    # Let's check signal for 'close' or 'price'.
    
    current_price = signal.get("metadata", {}).get("close")
    if current_price is None:
        # Fallback: We can't calculate exact SL price without reference.
        # But we can return an Intent that says "Entry + X pips".
        # For simplicity of this function returning FLOATS, let's assume 
        # we NEED price. If missing, fail or mock (for testing).
        # In real flow, risk_eval runs AFTER getting a quote or with the signal candle close.
        return OrderIntent(
            valid=False, symbol=symbol, direction=direction,
            size=0.0, sl_price=0.0, tp_price=0.0,
            reason="MISSING_REFERENCE_PRICE_IN_SIGNAL"
        )
        
    sl_pips = config.sl_pips_default
    tp_pips = config.tp_pips_default
    pip_size = 0.0001 # Standard for pairs like EURUSD
    
    if direction == "BUY":
        sl_price = current_price - (sl_pips * pip_size)
        tp_price = current_price + (tp_pips * pip_size)
    else: # SELL
        sl_price = current_price + (sl_pips * pip_size)
        tp_price = current_price - (tp_pips * pip_size)

    # 3. Position Sizing
    equity = account_snapshot.get("equity", 0.0)
    size = calculate_position_size(equity, config.risk_per_trade_pct, sl_pips)
    
    if size <= 0:
         return OrderIntent(
            valid=False, symbol=symbol, direction=direction,
            size=0.0, sl_price=0.0, tp_price=0.0,
            reason="CALCULATED_SIZE_ZERO"
        )

    # 4. Exposure Check
    exposure_check = check_exposure_limits(account_snapshot, size, config)
    if not exposure_check["allowed"]:
         return OrderIntent(
            valid=False, symbol=symbol, direction=direction,
            size=0.0, sl_price=0.0, tp_price=0.0,
            reason=exposure_check["reason"]
        )

    return OrderIntent(
        valid=True,
        symbol=symbol,
        direction=direction,
        size=size,
        sl_price=round(sl_price, 5),
        tp_price=round(tp_price, 5),
        reason="OK"
    )
