from typing import Tuple, Dict, Any, Union, Optional
from execution.config import config
from execution.models import OrderSide

# Constants
RISK_PERCENT = config.RISK_CONFIG.risk_per_trade_pct / 100.0 if config.RISK_CONFIG else 0.02
LOT_SIZE = 100_000
MIN_LOT_SIZE = 0.01

# Pip Values (Approximate/Baseline)
PIP_VALUE_JPY = 6.5   # $ per lot per pip for JPY pairs (fallback)
PIP_VALUE_USD = 10.0  # $ per lot per pip for USD quote pairs

def _normalize_signal(signal: Any) -> Dict[str, Any]:
    """Helper to convert Signal object to dictionary safely."""
    if isinstance(signal, dict):
        return signal
    
    # Try pydantic v2
    if hasattr(signal, "model_dump"):
        d = signal.model_dump()
    # Try pydantic v1
    elif hasattr(signal, "dict"):
        d = signal.dict()
    # Try __dict__ fallback
    elif hasattr(signal, "__dict__"):
        d = signal.__dict__.copy()
    else:
        return {} # Invalid
        
    # Ensure direction is present (Signal property)
    if "direction" not in d:
        if hasattr(signal, "direction"):
             d["direction"] = signal.direction
        elif "signal_type" in d:
             d["direction"] = d["signal_type"]
             
    return d

def risk_eval(signal: Union[Dict[str, Any], Any], account_snapshot: Dict[str, float]) -> Tuple[bool, str, float]:
    """
    Evaluates risk and calculates a recommended position size.
    
    Returns:
        (is_safe, reason, recommended_size_lots)
    """
    # Normalize signal input to dict
    signal = _normalize_signal(signal)

    # 0. Basic Validation
    is_valid, validation_msg = _validate_signal(signal, account_snapshot)
    if not is_valid:
        return False, validation_msg, 0.0

    # 1. Calculate Risk Amount ($)
    equity = account_snapshot.get('equity', 0.0)
    risk_amount = equity * RISK_PERCENT

    # 2. Get SL Distance (Pips)
    entry = signal.get('entry_price')
    sl = signal.get('stop_loss')
    symbol = signal.get('symbol', 'USDJPY')
    
    sl_pips, pip_error = _calculate_sl_pips(entry, sl, symbol)
    if pip_error:
        return False, pip_error, 0.0
    
    # 3. Pip Value & Lot Calculation
    pip_value_per_lot = _get_pip_value(symbol, entry)
    
    if sl_pips == 0 or pip_value_per_lot == 0:
        return False, "Invalid Risk Parameters (Zero Division)", 0.0

    try:
        # Standard Formula: Lots = RiskAmount / (StopLossPips * PipValuePerLot)
        raw_size = risk_amount / (sl_pips * pip_value_per_lot)
    except ZeroDivisionError:
        return False, "Zero Division in Size Calc", 0.0

    # 4. Rounding & Limits
    position_size = round(raw_size, 2)
    
    if position_size < MIN_LOT_SIZE:
        return False, f"Calculated Size {position_size} < Min {MIN_LOT_SIZE}", 0.0

    return True, f"Risk Approved: {position_size} lots ({risk_amount:.2f}$ Risk)", position_size

def _validate_signal(signal: Dict[str, Any], account: Dict[str, float]) -> Tuple[bool, str]:
    if not signal:
        return False, "No signal provided"
        
    direction = signal.get('direction')
    # Use Enum value or string check
    if direction == OrderSide.HOLD.value or direction == "HOLD":
        return False, "Signal is HOLD"
    
    equity = account.get('equity', 0)
    if equity <= 0:
        return False, "Insufficient Equity"
        
    entry = signal.get('entry_price')
    sl = signal.get('stop_loss')
    if not entry or not sl:
        return False, "Missing Entry/SL in Signal"
        
    return True, ""

def get_point_size(symbol: str) -> float:
    """Returns the point size for a given symbol (e.g. 0.01 for JPY, 0.0001 for others)."""
    return 0.01 if "JPY" in symbol else 0.0001

def _calculate_sl_pips(entry: float, sl: float, symbol: str) -> Tuple[float, str]:
    distance = abs(entry - sl)
    if distance == 0:
        return 0.0, "Invalid SL Distance (0)"
        
    point_size = get_point_size(symbol)
    
    sl_pips = distance / point_size
    return sl_pips, ""

def _get_pip_value(symbol: str, price: float) -> float:
    if "JPY" in symbol:
        # Dynamic approximate calculation for JPY pairs
        # Value per pip per lot = (0.01 / ExchangeRate) * 100,000
        if price > 0:
            return (0.01 / price) * LOT_SIZE
        else:
            return PIP_VALUE_JPY # Fallback
    else:
        # Assuming USD Quote (EURUSD, GBPUSD etc)
        # Value per pip per lot = 10 USD (standard)
        return PIP_VALUE_USD
