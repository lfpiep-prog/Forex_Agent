# conftest.py - Pytest Fixtures für Forex Agent Tests
# Erstellt: 2026-01-25

import sys
import os
import pytest
import pandas as pd
from datetime import datetime, timezone
from unittest.mock import MagicMock

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================
# Factory Functions (gemäß testing-patterns Skill)
# ============================================================

@pytest.fixture
def mock_candle_data():
    """Factory für OHLCV Kerzen-Daten."""
    def _make_candles(
        symbol: str = "USDJPY",
        count: int = 200,
        start_price: float = 158.0
    ) -> pd.DataFrame:
        import numpy as np
        np.random.seed(42)
        
        timestamps = pd.date_range(
            end=datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0),
            periods=count,
            freq='1H'
        )
        
        prices = start_price + np.cumsum(np.random.randn(count) * 0.1)
        
        return pd.DataFrame({
            'timestamp': timestamps,
            'symbol': symbol,
            'open': prices,
            'high': prices + np.random.rand(count) * 0.2,
            'low': prices - np.random.rand(count) * 0.2,
            'close': prices + np.random.randn(count) * 0.05,
            'volume': np.random.randint(1000, 10000, count)
        })
    
    return _make_candles


@pytest.fixture
def mock_signal():
    """Factory für Trading Signals."""
    def _make_signal(
        direction: str = "LONG",
        symbol: str = "USDJPY",
        entry_price: float = 158.0,
        stop_loss: float = 157.5,
        take_profit: float = 159.0
    ) -> dict:
        return {
            'timestamp': datetime.now(timezone.utc),
            'symbol': symbol,
            'direction': direction,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'rationale': f"Test signal: {direction}"
        }
    
    return _make_signal


@pytest.fixture
def mock_balance():
    """Factory für Account Balance Daten."""
    def _make_balance(
        balance: float = 10000.0,
        equity: float = 10000.0,
        daily_loss: float = 0.0
    ) -> dict:
        return {
            'balance': balance,
            'equity': equity,
            'daily_loss': daily_loss
        }
    
    return _make_balance


@pytest.fixture
def mock_broker():
    """Mock Broker für Tests ohne echte API-Calls."""
    broker = MagicMock()
    broker.get_balance.return_value = {
        'balance': 10000.0,
        'equity': 10000.0,
        'daily_loss': 0.0
    }
    broker.execute_order.return_value = {
        'status': 'FILLED',
        'order_id': 'TEST-123'
    }
    return broker


# ============================================================
# State Management
# ============================================================

@pytest.fixture
def clean_state(tmp_path):
    """Temporäres State-File für Idempotenz-Tests."""
    state_file = tmp_path / "test_state.json"
    yield str(state_file)
    # Cleanup happens automatically with tmp_path


# ============================================================
# Config Override
# ============================================================

@pytest.fixture
def test_config(monkeypatch):
    """Override config für Tests."""
    monkeypatch.setenv("IG_ACC_TYPE", "DEMO")
    monkeypatch.setenv("LIVE_TRADING_ENABLED", "false")
    yield
