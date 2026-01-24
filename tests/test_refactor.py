import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution.models import OrderIntent, OrderResult
from execution import risk
from execution.execute_order import ExecutionRouter
from execution.brokers.ig_broker import IGBroker

class TestRefactor(unittest.TestCase):
    def test_risk_eval_safe(self):
        """Test risk evaluation returns correct tuple structure."""
        signal = {
            'entry_price': 150.00,
            'stop_loss': 149.50,
            'direction': 'LONG',
            'symbol': 'USDJPY'
        }
        account = {'equity': 10000.0}
        
        is_safe, reason, lots = risk.risk_eval(signal, account)
        
        print(f"Risk Result: Safe={is_safe}, Reason={reason}, Lots={lots}")
        self.assertTrue(is_safe)
        self.assertGreater(lots, 0)
        self.assertIsInstance(lots, float)

    def test_execution_router(self):
        """Test execution router uses models correctly."""
        mock_broker = MagicMock()
        mock_broker.execute_order.return_value = OrderResult(status="FILLED", filled_quantity=1.0)
        
        router = ExecutionRouter(mock_broker)
        intent = OrderIntent("key123", "USDJPY", "LONG", 1.0)
        
        result = router.execute_order(intent)
        
        self.assertEqual(result.status, "FILLED")
        mock_broker.execute_order.assert_called_once_with(intent)

    @patch('execution.run_cycle._fetch_data')
    @patch('execution.run_cycle._check_time')
    def test_run_cycle_imports(self, mock_check_time, mock_fetch):
        """Test validation of run_cycle imports and basic flow."""
        from execution import run_cycle
        self.assertTrue(hasattr(run_cycle, '_assess_risk'))

if __name__ == '__main__':
    unittest.main()
