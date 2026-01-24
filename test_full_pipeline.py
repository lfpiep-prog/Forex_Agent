"""
End-to-End Pipeline Test Script
Tests: Config -> Data Fetch -> Signal Generation -> Risk Eval (No Execution)
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

print("=" * 50)
print("  FULL PIPELINE TEST (No Live Trading)")
print("=" * 50)

# 1. Config Check
print("\n[1/5] Checking Configuration...")
from execution.config import config
print(f"  SYMBOL: {config.SYMBOL}")
print(f"  TIMEFRAME: {config.TIMEFRAME}")
print(f"  STRATEGY: {config.STRATEGY}")
print(f"  DATA_PROVIDER: {config.DATA_PROVIDER}")
print(f"  BROKER: {config.BROKER}")

if config.DATA_PROVIDER.lower() != "twelvedata":
    print("  ERROR: DATA_PROVIDER is not 'twelvedata'. Check .env!")
    sys.exit(1)
print("  --> Config OK")

# 2. Data Fetch Test
print("\n[2/5] Fetching Data via TwelveData...")
from execution import market_data as data
raw_prices = data.fetch_prices(config.SYMBOL, config.TIMEFRAME, limit=50)
print(f"  Received {len(raw_prices)} candles.")

if not raw_prices:
    print("  ERROR: No data returned! Check API key or internet.")
    sys.exit(1)
print("  --> Data Fetch OK")

# 3. Normalize
print("\n[3/5] Normalizing Data...")
df = data.normalize(raw_prices)
print(f"  DataFrame shape: {df.shape}")
print(f"  Columns: {list(df.columns)}")
print(f"  Last close: {df['close'].iloc[-1]:.5f}")
print("  --> Normalization OK")

# 4. Signal Generation
print("\n[4/5] Generating Signals...")
from execution.generate_signals import SignalGenerator
engine = SignalGenerator(config.STRATEGY, config.STRATEGY_PARAMS)
signals = engine.generate(df)
print(f"  Generated {len(signals)} signals from history.")

if signals:
    last = signals[-1]
    print(f"  Latest Signal: {last['direction']} @ {last['timestamp']}")
    print(f"  Entry: {last['entry_price']:.5f}, SL: {last['stop_loss']:.5f}, TP: {last['take_profit']:.5f}")
else:
    print("  No signal at current candle (Normal, strategy waits for crossover).")
print("  --> Signal Engine OK")

# 5. Risk Evaluation (Dry Run)
print("\n[5/5] Risk Evaluation (Mock Account)...")
from execution import risk
mock_account = {"balance": 30000, "equity": 30000, "open_positions": 0, "daily_loss": 0}
if signals:
    is_safe, reason = risk.risk_eval(signals[-1], mock_account)
    print(f"  Trade Allowed: {is_safe}")
    print(f"  Reason: {reason}")
else:
    print("  Skipped (No signal to evaluate).")
print("  --> Risk Module OK")

print("\n" + "=" * 50)
print("  ALL CHECKS PASSED - READY FOR OVERNIGHT RUN")
print("=" * 50)
