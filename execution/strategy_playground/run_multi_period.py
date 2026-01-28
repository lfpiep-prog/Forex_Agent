import sys
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

# Load env before imports that might need it
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backtesting import Backtest
from execution.strategy_playground.loader import load_data
from execution.strategy_playground.strategies.alligator_trend import AlligatorTrendStrategy
import pandas as pd

def run_tests():
    # Setup periods
    end_date = datetime.now()
    periods = {
        "6 Months": end_date - relativedelta(months=6),
        "1 Year": end_date - relativedelta(years=1),
        "2 Years": end_date - relativedelta(years=2)
    }
    
    symbol = "USDJPY"
    
    print(f"========================================")
    print(f"STRATEGY TEST CENTER: Alligator Trend (Optimized)")
    print(f"Symbol: {symbol}")
    print(f"Ends: {end_date.strftime('%Y-%m-%d')}")
    print(f"========================================\n")

    for name, start_date in periods.items():
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        print(f"--- Running {name} Test ({start_str} to {end_str}) ---")
        
        try:
            # 1. Fetch Data
            # Timeframe: hour (H1)
            df = load_data(symbol, start_str, end_str, timeframe='hour', multiplier=1)
            
            if df.empty:
                print(f"[X] No data found for {name} period.")
                continue
                
            print(f"Loaded {len(df)} candles.")

            # 2. Run Backtest
            # Margin=0.02 means 50:1 leverage.
            bt = Backtest(df, AlligatorTrendStrategy, cash=10000, commission=.0002, margin=0.02)
            stats = bt.run()
            
            # 3. Print Key Metrics
            print(f"Return [%]: {stats['Return [%]']:.2f}%")
            print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
            print(f"Max Drawdown [%]: {stats['Max. Drawdown [%]']:.2f}%")
            print(f"Trades: {stats['# Trades']}")
            print(f"Win Rate [%]: {stats['Win Rate [%]']:.2f}%")
            print(f"----------------------------------------\n")
            
        except Exception as e:
            print(f"[X] Error running {name}: {e}")
            import traceback
            traceback.print_exc()
            print("\n")

if __name__ == "__main__":
    run_tests()
