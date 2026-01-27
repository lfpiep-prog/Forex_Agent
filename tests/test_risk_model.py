
import pytest
from datetime import datetime
from execution.risk import risk_eval
from execution.core.signals import Signal, SignalType

def test_risk_eval_with_signal_object():
    # Create a Signal object
    signal = Signal(
        symbol="USDJPY",
        timestamp=datetime.now(),
        signal_type=SignalType.LONG,
        entry_price=100.0,
        stop_loss=99.0,
        take_profit=102.0,
        rationale="Test"
    )
    
    # Create account snapshot
    account = {
        "equity": 10000.0
    }
    
    # Run risk_eval
    # This would crash before the fix with "AttributeError: 'Signal' object has no attribute 'get'"
    is_safe, reason, lots = risk_eval(signal, account)
    
    # Verify it ran effectively
    assert isinstance(is_safe, bool)
    assert isinstance(reason, str)
    assert isinstance(lots, float)
    
    # Check if calculation is somewhat correct (Risk 2% of 10000 = 200. USDJPY pip value approx 6.5.
    # Entry 100, SL 99 -> 1.0 distance. Point size 0.01 -> 100 pips.
    # Risk = 200. Pips = 100. ValPerPip = ~6.5.
    # 200 / (100 * 6.5) = 200 / 650 = ~0.3
    
    print(f"Lots: {lots}")
    assert lots > 0

if __name__ == "__main__":
    test_risk_eval_with_signal_object()
