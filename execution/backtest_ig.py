
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution.brokers.ig_broker import IGBroker
from execution.backtest_run import run_single_backtest  # Reuse logic
from execution.generate_signals import SignalGenerator

def fetch_ig_history(symbol="USDJPY", limit=6000):
    print(f"--- Fetching {limit} candles (1H) for {symbol} from IG ---")
    
    broker = IGBroker()
    if not broker.connect():
        print("Could not connect to IG to fetch data.")
        return pd.DataFrame()

    epic = broker._find_epic(symbol) or "CS.D.USDJPY.MINI.IP"
    
    try:
        # Fetch data
        # '1H' resolution
        res = broker.ig_service.fetch_historical_prices_by_epic_and_num_points(
            epic, 
            resolution='1H', 
            numpoints=limit
        )
        
        df = res['prices']
        
        # Normalize
        # Structure is MultiIndex: (bid, ask, last) x (Open, High, Low, Close)
        # We will use BID prices for backtesting (standard convention)
        
        # Check if MultiIndex
        if isinstance(df.columns, pd.MultiIndex):
            # Extract Bid
            df_bid = df['bid'].copy()
        else:
            # Fallback if flat (unlikely based on test)
            df_bid = df
            
        df_bid = df_bid.reset_index()
        
        normalized = []
        for _, row in df_bid.iterrows():
            # DateTime is in index or column? After reset_index, it's a column 'DateTime'
            ts = row['DateTime']
            
            normalized.append({
                "timestamp": pd.to_datetime(ts),
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": float(res['prices']['last']['Volume'].iloc[_]) if 'last' in df.columns and 'Volume' in df.columns.get_level_values(1) else 0,
                "symbol": symbol
            })
            
        return pd.DataFrame(normalized)
        
    except Exception as e:
        print(f"Error fetching IG history: {e}")
        return pd.DataFrame()

def run_ig_tournament():
    print("--- Starting Backtest with IG Broker Data ---")
    
    champions = [
        {"symbol": "USDJPY", "name": "SMA 10/30 (Aggressive)", "fast_period": 10, "slow_period": 30, "use_rsi_filter": False},
        {"symbol": "USDJPY", "name": "SMA 10/30 + RSI",        "fast_period": 10, "slow_period": 30, "use_rsi_filter": True},
        # Add a GBPUSD config if we want, but sticking to USDJPY for now or need epic
        # {"symbol": "GBPUSD", "name": "SMA 20/50 (Balanced)",   "fast_period": 20, "slow_period": 50, "use_rsi_filter": False},
    ]
    
    # 1. Fetch Data Once
    symbol = "USDJPY"
    df_prices = fetch_ig_history(symbol, limit=6000)
    
    if df_prices.empty:
        print("No data fetched. Aborting.")
        return

    print(f"Loaded {len(df_prices)} candles. Date Range: {df_prices['timestamp'].min()} to {df_prices['timestamp'].max()}")

    # 2. Run Tests
    start_bal = 10000.0
    results = []
    
    for cfg in champions:
        if cfg['symbol'] != symbol: continue # Skip if different symbol for this run
        
        print(f"\nTesting {cfg['name']}...")
        
        engine = SignalGenerator("baseline_sma_cross", {k: v for k, v in cfg.items() if k not in ['name', 'symbol']})
        signals = engine.generate(df_prices)
        
        # Simulate Compounding
        current_balance = start_bal
        wins, losses = 0, 0
        
        for sig in signals:
            # Risk 2%
            risk_amt = current_balance * 0.02
            entry = sig['entry_price']
            sl = sig['stop_loss']
            tp = sig['take_profit']
            direction = sig['direction']
            
            # Outcome
            timestamp = sig['timestamp']
            # Find index
            try:
                idx = df_prices[df_prices['timestamp'] == timestamp].index[0]
            except: continue
            
            future = df_prices.iloc[idx+1:]
            
            outcome = None
            pnl_usd = 0
            
            for _, row in future.iterrows():
                if direction == 'LONG':
                    if row['low'] <= sl:
                        outcome = "LOSS"; pnl_usd = -risk_amt; break
                    elif row['high'] >= tp:
                        outcome = "WIN"; pnl_usd = risk_amt * 2.0; break
                else:
                    if row['high'] >= sl:
                        outcome = "LOSS"; pnl_usd = -risk_amt; break
                    elif row['low'] <= tp:
                        outcome = "WIN"; pnl_usd = risk_amt * 2.0; break
            
            if outcome:
                current_balance += pnl_usd
                if outcome == "WIN": wins += 1
                else: losses += 1
        
        total = wins + losses
        wr = (wins/total*100) if total else 0
        growth = ((current_balance - start_bal) / start_bal) * 100
        
        results.append({
            "Strategy": cfg['name'],
            "Trades": total,
            "Win Rate": f"{wr:.1f}%",
            "End Balance": f"${current_balance:,.2f}",
            "Growth": f"{growth:.1f}%"
        })

    # Output
    print("\n" + "="*80)
    res_df = pd.DataFrame(results)
    print(res_df.to_string(index=False))
    print("="*80)

if __name__ == "__main__":
    run_ig_tournament()
