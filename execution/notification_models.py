"""
Notification Models - Validated payloads for Discord notifications.

Ensures correct field population from the appropriate data sources.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class TradeNotificationPayload:
    """
    Validated payload for trade notifications.
    
    This dataclass ensures the notification uses the correct data sources:
    - SUBMITTED: Uses requested_entry (signal price) since fill hasn't occurred
    - FILLED: Uses fill_price from broker response
    """
    # Required Fields
    symbol: str
    direction: str  # LONG, SHORT
    status: str     # SUBMITTED, FILLED, REJECTED, FAILED
    
    # Order Intent Data (from signal/order_intent)
    requested_size: float
    requested_entry: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Execution Result Data (from broker response, populated for FILLED)
    fill_price: Optional[float] = None
    fill_quantity: Optional[float] = None
    fill_time: Optional[datetime] = None
    
    # IDs and Metadata
    broker_order_id: Optional[str] = None
    rationale: str = ""
    signal_time: Optional[datetime] = None
    error_message: Optional[str] = None
    
    def get_display_price(self) -> str:
        """Returns the appropriate price to display based on status."""
        if self.status == "FILLED" and self.fill_price is not None:
            return f"{self.fill_price}"
        elif self.requested_entry is not None:
            return f"{self.requested_entry}"
        return "N/A"
    
    def get_display_size(self) -> str:
        """Returns the appropriate size to display based on status."""
        if self.status == "FILLED" and self.fill_quantity is not None:
            return f"{self.fill_quantity} lots"
        return f"{self.requested_size} lots"
    
    def validate(self) -> list[str]:
        """Returns list of validation warnings for missing fields."""
        warnings = []
        if not self.symbol:
            warnings.append("symbol is empty")
        if not self.direction:
            warnings.append("direction is empty")
        if not self.status:
            warnings.append("status is empty")
        if self.requested_size <= 0:
            warnings.append(f"requested_size is invalid: {self.requested_size}")
        if self.status == "FILLED" and self.fill_price is None:
            warnings.append("FILLED status but fill_price is None")
        return warnings
