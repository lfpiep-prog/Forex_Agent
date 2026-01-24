import random

def execute_order(order_payload):
    """
    Simulates sending an order to the broker (e.g., IBKR, OANDA).
    """
    # Simulate network latency or processing
    
    # Mock response
    success = random.choice([True, True, True, False]) # 75% success chance
    
    if success:
        return {
            "status": "FILLED",
            "order_id": f"ORD-{random.randint(1000, 9999)}",
            "filled_price": order_payload.get("price"),
            "timestamp": order_payload.get("timestamp")
        }
    else:
        return {
            "status": "REJECTED",
            "reason": "Broker API timeout or insufficient funds"
        }
