import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

# Add project root to sys.path to ensure we can import execution modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backtesting import Backtest
from execution.strategy_playground.loader import load_data
from execution.strategy_playground.strategies.sma_cross import SmaCross
import pandas as pd

def run_strategy(symbol="EURUSD", start="2025-01-01", end="2025-01-25"):
    print(f"--- Running Backtest for {symbol} ---")
    print(f"Period: {start} to {end}")
    
    # 1. Load Data
    # Fetching 1-hour candles: timespan='hour', multiplier=1
    # OR timespan='minute', multiplier=60
    df = load_data(symbol, start, end, timeframe='hour', multiplier=1)
    
    if df.empty:
        print("Error: No data fetched.")
        return

    print(f"Data Loaded: {len(df)} candles")
    print(df.head())

    # 2. Setup Backtest
    bt = Backtest(df, SmaCross, cash=10000, commission=.0002, exclusive_orders=True)

    # 3. Run
    stats = bt.run()
    
    # 4. Print Results
    print("\n--- Results ---")
    print(stats)
    
    # Optional: Plot
    # bt.plot() # This opens a browser window, might not work well in headless/agent env.

if __name__ == "__main__":
    run_strategy()
