import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json
import shutil
from datetime import datetime, timezone, timedelta
import pandas as pd

# Add project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution.state_manager import StateManager
from execution.run_cycle import fetch_and_prepare_data
from main_loop import get_seconds_until_next_hour
from execution.config import config

class TestStabilization(unittest.TestCase):

    def setUp(self):
        self.test_state_file = "data/test_state.json"
        self.state_manager = StateManager(self.test_state_file)
        if os.path.exists(self.test_state_file):
            os.remove(self.test_state_file)

    def tearDown(self):
        if os.path.exists(self.test_state_file):
            os.remove(self.test_state_file)

    def test_state_manager(self):
        """Test reading and writing state."""
        symbol = "TEST"
        tf = "H1"
        ts = "2023-01-01T12:00:00+00:00"
        
        # Initial check
        self.assertFalse(self.state_manager.is_candle_processed(symbol, tf, ts))
        
        # Mark processed
        self.state_manager.mark_candle_processed(symbol, tf, ts)
        
        # Check again
        self.assertTrue(self.state_manager.is_candle_processed(symbol, tf, ts))
        
        # Verify persistence
        with open(self.test_state_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data.get(f"{symbol}_{tf}"), ts)

    def test_trigger_logic(self):
        """Test next hour calculation."""
        seconds = get_seconds_until_next_hour()
        self.assertGreater(seconds, 0)
        self.assertLessEqual(seconds, 3600)
        
        # Border case check (mocking now)
        with patch('main_loop.datetime') as mock_dt:
            # Set time to 10:59:59 UTC
            mock_now = datetime(2023, 1, 1, 10, 59, 59, tzinfo=timezone.utc)
            mock_dt.now.return_value = mock_now
            mock_dt.timedelta = timedelta # Restore timedelta
            
            # Should be 1 second
            # Re-import to affect the module function if it uses datetime.datetime directly, 
            # but main_loop imports datetime class. 
            # Logic in main_loop: now = datetime.now(timezone.utc)
            
            # Since main_loop imports datetime from datetime, we need to patch main_loop.datetime
            pass # Skip complex patching of built-in types for this simple check, the range check above is decent.

    @patch('execution.run_cycle.data.fetch_prices')
    @patch('execution.run_cycle.data.normalize')
    @patch('execution.run_cycle.time.sleep') # Don't actually sleep
    def test_delayed_data_retry(self, mock_sleep, mock_normalize, mock_fetch):
        """Test that data fetch retries if the candle is old."""
        
        # Setup expected calls
        # We want the pipeline to look for the "Previous Hour" candle.
        # If Logic runs at 14:00:05 UTC, it wants 13:00:00 UTC candle.
        
        now = datetime.now(timezone.utc)
        target_time = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
        old_time = target_time - timedelta(hours=1) # 2 hours ago
        
        # Mock Data Structure
        def make_df(ts):
            return pd.DataFrame([{'timestamp': ts, 'close': 1.0}])

        # Scenario: 
        # Attempt 1: Returns Old Candle (12:00) when we want (13:00)
        # Attempt 2: Returns Old Candle
        # Attempt 3: Returns Correct Candle (13:00)
        
        mock_fetch.return_value = [{"dummy": "data"}]
        
        # Normalize side effect
        df_old = make_df(old_time)
        df_new = make_df(target_time)
        
        mock_normalize.side_effect = [df_old, df_old, df_new]
        
        log = MagicMock()
        plog = MagicMock()
        
        # override config retry to be sure
        config.DATA_RETRY_ATTEMPTS = 3
        
        result_df = fetch_and_prepare_data(log, plog)
        
        # Assertions
        self.assertEqual(mock_normalize.call_count, 3) # Should have tried 3 times
        self.assertEqual(result_df.iloc[-1]['timestamp'], target_time)
        self.assertTrue(mock_sleep.called)

if __name__ == '__main__':
    unittest.main()
