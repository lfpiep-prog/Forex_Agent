
import logging
import uuid
import time
from datetime import datetime
from .base_broker import BaseBroker
# We need to import OrderResult from the parent package, but for now we'll assume it's available or re-define if strictly needed to avoid circular dep issues in simple script
# For simplicity in this file, we will try to import from the execution module relative path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from execution.execute_order import OrderIntent, OrderResult

logger = logging.getLogger("MockBroker")

class MockBroker(BaseBroker):
    """
    Simulates a broker for Paper Trading / Backtesting.
    Fills orders immediately with simulated slippage (optional).
    """
    def __init__(self, slip_probability=0.0, slip_amount=0.0):
        self.slip_probability = slip_probability
        self.slip_amount = slip_amount
        logger.info("MockBroker initialized.")

    def connect(self):
        return True

    def get_balance(self):
        """Mock balance"""
        return {
            "balance": 10000.0,
            "equity": 10000.0,
            "available": 10000.0
        }

    def execute_order(self, intent: OrderIntent) -> OrderResult:
        logger.info(f"MockBroker routing: {intent.direction} {intent.quantity} {intent.symbol}")
        
        # Simulate Network Latency
        time.sleep(0.1) 
        
        # Simulate Fill
        # In a real backtest, we'd check current price. 
        # For MVP paper trading, we assume we fill at 'current market price' or limit price.
        # Since we don't have the live price feed *here* in this method easily without passing it,
        # we might assume the Limit Price is the fill price (if LIMIT) or fetch latest from a data source.
        # For MVP, let's assume fill_price = intent.limit_price if provided else 1.0 (placeholder)
        
        fill_price = intent.limit_price if intent.limit_price else 1.0500 # Default dummy price
        
        # Generate a fake broker Order ID
        mock_id = f"mock_{uuid.uuid4().hex[:8]}"
        
        return OrderResult(
            status="FILLED",
            broker_order_id=mock_id,
            filled_price=fill_price,
            filled_quantity=intent.quantity,
            timestamp=datetime.utcnow(),
            raw_response={"message": "Mock fill success"}
        )

    def get_status(self, broker_order_id: str) -> OrderResult:
        # Mock always returns filled for past orders
        return OrderResult(status="FILLED", filled_quantity=0, timestamp=datetime.utcnow())
