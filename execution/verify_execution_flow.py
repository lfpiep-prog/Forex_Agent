
import sys
import os
import logging
import uuid
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from execution.execute_order import ExecutionRouter, OrderIntent
from execution.brokers.mock_broker import MockBroker

def verify_execution():
    print("--- Starting Execution Verification ---")
    
    # 1. Setup
    mock_broker = MockBroker()
    router = ExecutionRouter(mock_broker)
    
    # 2. Create Order Intent
    intent_id = str(uuid.uuid4())
    intent = OrderIntent(
        idempotency_key=intent_id,
        symbol="EUR_USD",
        direction="BUY",
        quantity=10000,
        order_type="MARKET"
    )
    print(f"Created Intent: {intent}")
    
    # 3. Execute First Time
    print("Executing Order (1st attempt)...")
    result1 = router.execute_order(intent)
    print(f"Result 1: {result1}")
    
    if result1.status != "FILLED":
        print("FAIL: Order was not FILLED.")
        return False
        
    if result1.filled_quantity != 10000:
        print("FAIL: Incorrect filled quantity.")
        return False

    # 4. Idempotency Check (Execute same intent again)
    print("Executing Order (2nd attempt - Idempotency Check)...")
    result2 = router.execute_order(intent)
    print(f"Result 2: {result2}")
    
    if result2.broker_order_id != result1.broker_order_id:
        print("FAIL: Idempotency failed. Different Broker Order IDs.")
        return False
        
    print("SUCCESS: Execution and Idempotency verified.")
    return True

if __name__ == "__main__":
    verify_execution()
