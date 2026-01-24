from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class OrderIntent:
    """
    Represents an intent to execute a trade order.
    """
    idempotency_key: str
    symbol: str
    direction: str  # "BUY" or "SELL", or "LONG"/"SHORT"
    quantity: float # Lots/Contracts
    order_type: str = "MARKET"
    limit_price: Optional[float] = None
    sl_distance: Optional[float] = None
    tp_distance: Optional[float] = None
    created_at: datetime = datetime.utcnow()

@dataclass
class OrderResult:
    """
    Represents the result of an order execution attempt.
    """
    status: str  # "ACCEPTED", "FILLED", "REJECTED", "FAILED", "SUBMITTED"
    broker_order_id: Optional[str] = None
    filled_price: Optional[float] = None
    filled_quantity: float = 0.0
    timestamp: datetime = datetime.utcnow()
    error_message: Optional[str] = None
    raw_response: Optional[dict] = None
