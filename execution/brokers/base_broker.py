
from abc import ABC, abstractmethod
from typing import Any
import sys
import os

# Ensure we can import OrderIntent and OrderResult
# Assuming execute_order.py is in the parent directory 'execution'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from execution.execute_order import OrderIntent, OrderResult
except ImportError:
    # If running as a standalone script or package issues, might need adjustment
    pass

class BaseBroker(ABC):
    """
    Abstract base class for all broker implementations.
    """
    
    @abstractmethod
    def execute_order(self, intent: Any) -> Any:
        # returns OrderResult
        pass

    @abstractmethod
    def get_status(self, broker_order_id: str) -> Any:
        pass
