import logging
import time
from typing import Dict
from datetime import datetime
from execution.models import OrderIntent, OrderResult

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ExecutionRouter")

class ExecutionRouter:
    """
    Routes orders to the configured broker and handles basic idempotency and retries.
    """
    def __init__(self, broker_instance):
        self.broker = broker_instance
        # Simple in-memory idempotency check (Limit size to avoid memory leaks)
        self._processed_orders: Dict[str, OrderResult] = {} 
        self._max_cache_size = 1000

    def execute_order(self, intent: OrderIntent) -> OrderResult:
        """
        Routes the order to the configured broker.
        Ensures idempotency.
        """
        logger.info(f"Received Execution Request: {intent}")

        # Idempotency Check
        if intent.idempotency_key in self._processed_orders:
            logger.info(f"Idempotency hit for key: {intent.idempotency_key}. Returning cached result.")
            return self._processed_orders[intent.idempotency_key]

        result = self._execute_with_retry(intent)
        
        # Cache Result
        self._cache_result(intent.idempotency_key, result)
        
        logger.info(f"Execution Result for {intent.idempotency_key}: {result.status}")
        return result

    def _execute_with_retry(self, intent: OrderIntent) -> OrderResult:
        """
        Executes order with simple exponential backoff retry logic.
        """
        max_retries = 3
        
        for attempt in range(1, max_retries + 1):
            try:
                # Execute via Broker
                return self.broker.execute_order(intent)

            except Exception as e:
                logger.warning(f"Execution attempt {attempt} failed: {e}")
                
                if attempt == max_retries:
                    logger.error(f"Max retries reached. Execution Failed: {e}", exc_info=True)
                    return OrderResult(
                        status="FAILED",
                        error_message=str(e),
                        timestamp=datetime.utcnow()
                    )
                
                # Simple backoff: 0.5s, 1.0s, 2.0s...
                time.sleep(0.5 * (2 ** (attempt - 1)))
        
        # Should be unreachable given return in loop
        return OrderResult(status="FAILED", error_message="Unknown retry error")

    def _cache_result(self, key: str, result: OrderResult):
        """
        Caches the result, maintaining a maximum size limit.
        """
        if len(self._processed_orders) >= self._max_cache_size:
            # Simple eviction: remove one arbitrary item (FIFO in Python 3.7+)
            # Not optimally efficient for large caches but fine for this scale.
            self._processed_orders.pop(next(iter(self._processed_orders)))
            
        self._processed_orders[key] = result

if __name__ == "__main__":
    print("Execution Router Module Loaded")
