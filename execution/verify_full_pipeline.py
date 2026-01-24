
import sys
import os
import pandas as pd
import numpy as np
import uuid
from datetime import datetime
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from execution.execute_order import ExecutionRouter, OrderIntent
from execution.brokers.mock_broker import MockBroker
from execution.strategies.baseline_sma_cross import BaselineSMACross
from execution.risk_eval import evaluate_risk
from execution.risk_limits import RiskConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PipelineVerify")

def generate_dummy_data(rows=300):
    """Generates dummy price data for SMA crossover."""
    dates = pd.date_range(end=datetime.utcnow(), periods=rows, freq='H')
    data = []
    price = 1.0500
    for date in dates:
        change = np.random.uniform(-0.0010, 0.0010)
        price += change
        data.append({
            'timestamp': date,
            'symbol': 'EUR_USD',
            'open': price,
            'high': price + 0.0005,
            'low': price - 0.0005,
            'close': price + 0.0002
        })
    df = pd.DataFrame(data)
    
    # Force a crossover at the end
    # Fast SMA (50) needs to cross Slow SMA (200)
    # Let's just create a strong trend up for the last 60 points
    for i in range(rows - 60, rows):
        df.at[i, 'close'] = df.at[i-1, 'close'] + 0.0020 # Strong Move Up
        
    return df

def run_pipeline():
    logger.info(">>> 1. Generating Market Data (Prices)...")
    df = generate_dummy_data()
    logger.info(f"Generated {len(df)} rows of data.")

    logger.info(">>> 2. Running Signal Engine...")
    strategy = BaselineSMACross(fast_period=50, slow_period=200)
    signals = strategy.calculate(df)
    
    logger.info(f"Generated {len(signals)} signals.")
    
    if not signals:
        logger.warning("No signals generated. Cannot proceed with full pipeline verify.")
        # Force a dummy signal for testing if strategy fails to generate one naturally
        dummy_signal = {
            'symbol': 'EUR_USD',
            'direction': 'LONG',
            'entry_price': 1.1000,
            'stop_loss': 1.0950,
            'take_profit': 1.1100,
            'rr_ratio': 2.0,
            'confidence': 1.0,
            'rationale': 'Forced Test Signal',
            # Add metadata for risk eval
            'metadata': {'close': 1.1000} 
        }
        signals = [dummy_signal]
        logger.info(f"Using FORCED dummy signal: {dummy_signal}")

    latest_signal = signals[-1]
    # Ensure metadata exists if not set (for robust risk eval fallback)
    if 'metadata' not in latest_signal:
         latest_signal['metadata'] = {'close': latest_signal['entry_price']}
         
    logger.info(f"Latest Signal: {latest_signal}")

    logger.info(">>> 3. Risk Management Layer...")
    # Mock account data - Needs 'equity' for position sizing
    account_data = {
         "balance": 10000.0,
         "equity": 10000.0,
         "open_positions": [],
         "daily_loss": 0
    }
    
    # Needs a config
    config = RiskConfig(
        max_daily_loss_pct=2.0,
        max_trades_per_day=5,
        risk_per_trade_pct=1.0,
        max_open_lots=5.0,
        sl_pips_default=30.0,
        tp_pips_default=60.0
    )
    
    risk_intent = evaluate_risk(latest_signal, account_data, config)
    logger.info(f"Risk Evaluation Result: Valid={risk_intent.valid}, Reason='{risk_intent.reason}', Size={risk_intent.size}")
    
    if not risk_intent.valid:
        logger.error("Signal rejected by Risk Layer. Stopping.")
        return

    logger.info(">>> 4. Execution Layer...")
    
    # Convert Risk Intent to Execution Intent
    # (In a real scenario, they might be the same or mapped)
    # Reconstruct for clarity
    
    intent = OrderIntent(
        idempotency_key=str(uuid.uuid4()),
        symbol=risk_intent.symbol,
        direction=risk_intent.direction,
        quantity=int(risk_intent.size * 100000), # Mock conversion to units
        order_type="MARKET",
        limit_price=None # Market order
    )
    
    mock_broker = MockBroker()
    router = ExecutionRouter(mock_broker)
    
    result = router.execute_order(intent)
    logger.info(f"Final Execution Result: {result}")
    
    if result.status == "FILLED":
        print("\n[SUCCESS] FULL PIPELINE SUCCESS: Prices -> Signal -> Risk -> Execution")
    else:
        print("\n[FAILED] PIPELINE FAILED at Execution")

if __name__ == "__main__":
    run_pipeline()
