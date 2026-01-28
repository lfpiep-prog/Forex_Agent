import sys
import os
import pandas as pd
from backtesting import Backtest
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Assuming running from project root
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv(".env")

from execution.strategy_playground.loader import load_data
from execution.strategy_playground.strategies.alligator_trend import AlligatorTrendStrategy

def run_optimization():
    # Load 1 Year of Data for Optimization (Recent regime is most important)
    end_date = datetime.now()
    start_date = end_date - relativedelta(years=1)
    
    symbol = "USDJPY"
    print(f"Loading data for {symbol} optimization...")
    df = load_data(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), timeframe='hour', multiplier=1)
    
    if df.empty:
        print("No data.")
        return

    bt = Backtest(df, AlligatorTrendStrategy, cash=10000, commission=.0002, margin=0.02)
    
    print("Starting Optimization...")
    # Optimize Risk Parameters
    stats = bt.optimize(
        sl_atr_mult=[2.0, 3.0, 4.0],
        use_trailing_sl=[True, False],
        adx_threshold=[20, 25, 30],
        # Fixing TP since Trailing SL might override it or just high target
        maximize='Return [%]',
    )
    
    print("\n--- BEST RESULTS ---")
    print(stats)
    print("\n--- BEST PARAMETERS ---")
    print(stats._strategy)

if __name__ == "__main__":
    run_optimization()
