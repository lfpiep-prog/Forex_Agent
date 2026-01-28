from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum, auto

class OrderSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class OrderStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    FILLED = "FILLED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    SUBMITTED = "SUBMITTED"
    PENDING = "PENDING"

@dataclass
class OrderIntent:
    """
    Represents an intent to execute a trade order.
    """
    idempotency_key: str
    symbol: str
    direction: OrderSide
    quantity: float # Lots/Contracts
    order_type: OrderType = OrderType.MARKET
    limit_price: Optional[float] = None
    sl_distance: Optional[float] = None
    tp_distance: Optional[float] = None
    created_at: datetime = datetime.utcnow()

@dataclass
class OrderResult:
    """
    Represents the result of an order execution attempt.
    """
    status: OrderStatus
    broker_order_id: Optional[str] = None
    filled_price: Optional[float] = None
    filled_quantity: float = 0.0
    timestamp: datetime = datetime.utcnow()
    error_message: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
