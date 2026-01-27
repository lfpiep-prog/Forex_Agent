from typing import Dict, Optional, Union
from dataclasses import dataclass, asdict
from execution.risk_limits import RiskConfig, check_daily_limits, check_exposure_limits
from execution.core.signals import Signal, SignalType

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

def evaluate_risk(signal: Union[Signal, Dict], account_snapshot: Dict, config: RiskConfig) -> OrderIntent:
    """
    Main entry point to convert a Signal into an OrderIntent.
    Accepts both typed Signal objects and legacy dictionaries.
    """
    # Handle typed Signal objects
    if isinstance(signal, Signal):
        symbol = signal.symbol
        direction = signal.direction  # Uses property for backward compat
        current_price = signal.metadata.get("close") if signal.metadata else signal.entry_price
    else:
        # Legacy dict support
        symbol = signal.get("symbol", "UNKNOWN")
        direction = signal.get("direction", "BUY")
        current_price = signal.get("metadata", {}).get("close")
    
    # 1. Global Kill Switch / Daily Limits
    limit_check = check_daily_limits(account_snapshot, config)
    if not limit_check["allowed"]:
        return OrderIntent(
            valid=False, symbol=symbol, direction=direction, 
            size=0.0, sl_price=0.0, tp_price=0.0, 
            reason=limit_check["reason"]
        )

    # 2. Determine SL/TP
    if current_price is None:
        return OrderIntent(
            valid=False, symbol=symbol, direction=direction,
            size=0.0, sl_price=0.0, tp_price=0.0,
            reason="MISSING_REFERENCE_PRICE_IN_SIGNAL"
        )
        
    sl_pips = config.sl_pips_default
    tp_pips = config.tp_pips_default
    pip_size = 0.0001  # Standard for pairs like EURUSD
    
    # Map direction string to BUY/SELL for SL/TP calculation
    is_buy = direction in ("BUY", "LONG", SignalType.LONG.value)
    
    if is_buy:
        sl_price = current_price - (sl_pips * pip_size)
        tp_price = current_price + (tp_pips * pip_size)
    else:  # SELL / SHORT
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
