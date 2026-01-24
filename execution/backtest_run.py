import pandas as pd
import sys
import os
import time
from datetime import datetime
import numpy as np

# Add execution path to find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from market_data import fetch_prices, normalize
from generate_signals import SignalGenerator

def run_single_backtest(df, strategy_config):
    """
    Runs backtest for a single config on provided dataframe.
    """
    # Filter out non-param keys
    clean_config = {k: v for k, v in strategy_config.items() if k not in ['name', 'symbol']}
    engine = SignalGenerator("baseline_sma_cross", clean_config)
    signals = engine.generate(df)
    
    if not signals:
        return 0, 0, 0 # trades, win_rate, total_r

    trades = []
    
    for sig in signals:
        entry_time = sig['timestamp']
        entry_price = sig['entry_price']
        stop_loss = sig['stop_loss']
        take_profit = sig['take_profit']
        direction = sig['direction']
        
        # Find entry index
        try:
            entry_idx = df[df['timestamp'] == entry_time].index[0]
        except IndexError:
            continue
            
        future_data = df.iloc[entry_idx+1:]
        outcome = None
        pnl = 0
        
        for _, row in future_data.iterrows():
            if direction == 'LONG':
                if row['low'] <= stop_loss:
                    outcome = "LOSS"
                    pnl = -1.0
                    break
                elif row['high'] >= take_profit:
                    outcome = "WIN"
                    pnl = 2.0
                    break
            elif direction == 'SHORT':
                if row['high'] >= stop_loss:
                    outcome = "LOSS"
                    pnl = -1.0
                    break
                elif row['low'] <= take_profit:
                    outcome = "WIN"
                    pnl = 2.0
                    break
                elif row['low'] <= take_profit:
                    outcome = "WIN"
                    pnl = 2.0
                    break

        # Check for open trades
        if outcome is None and not future_data.empty:
            outcome = "OPEN"
            curr_price = df.iloc[-1]['close']
            if direction == 'LONG':
                dist_sl = max(0.0001, entry_price - stop_loss)
                pnl = (curr_price - entry_price) / dist_sl
            else:
                dist_sl = max(0.0001, stop_loss - entry_price)
                pnl = (entry_price - curr_price) / dist_sl

        trades.append({"outcome": outcome, "pnl": pnl})

    # Stats
    df_trades = pd.DataFrame(trades)
    closed_trades = df_trades[df_trades['outcome'] != 'OPEN']
    
    total_trades = len(closed_trades)
    if total_trades == 0:
        return 0, 0, 0
        
    wins = len(closed_trades[closed_trades['outcome'] == 'WIN'])
    win_rate = (wins / total_trades * 100)
    total_r = closed_trades['pnl'].sum()
    
    return total_trades, win_rate, total_r

def run_tournament():
    print("--- Starting Deep Backtest (H1 / 6000 candles / ~1 Year) ---")
    
    # The Top 3 Configurations from the previous round
    champions = [
        {"symbol": "USDJPY", "name": "SMA 10/30 (Aggressive)", "fast_period": 10, "slow_period": 30, "use_rsi_filter": False},
        {"symbol": "USDJPY", "name": "SMA 10/30 + RSI",        "fast_period": 10, "slow_period": 30, "use_rsi_filter": True},
        {"symbol": "GBPUSD", "name": "SMA 20/50 (Balanced)",   "fast_period": 20, "slow_period": 50, "use_rsi_filter": False},
    ]
    
    results = []
    
    # Iterate by symbol to minimize data fetching
    # Group configs by symbol
    from collections import defaultdict
    symbol_map = defaultdict(list)
    for c in champions:
        symbol_map[c['symbol']].append(c)
        
    for symbol, configs in symbol_map.items():
        print(f"\nFetching 6000 candles (1y) for {symbol}...")
        # Fetching 730 days to ensure we get ~6000 trading hours (24*5*52 is approx 6200)
        # Using 6000 limit in data fetching
        try:
            # Need to ensure fetch_prices supports larger limit/period
            # Calling directly here or updating data.py? 
            # fetch_prices uses "6mo" hardcoded in previous step. 
            # We will use a custom fetch here or rely on data.py update.
            # Let's call fetch with limit=6000, but data.py needs to handle the period="2y" to get enough data.
            # For now, let's update data.py to be dynamic or just patch it here.
            # Actually, let's just use yfinance directly here for the specific "Deep" need to avoid changing global data.py for now
             # OR update data.py to accept period. Let's update data.py first is cleaner.
             # But to save turns, I'll modify data.py import usage to pass period if I changed it.
             # existing data.py hardcodes period="6mo". I should change that.
             pass
        except:
             pass
             
    # WAIT: I need to update data.py to allow fetching 1y/2y data first, 
    # OR I can just override the fetch logic in this script.
    # Overriding here is safer for the "Test" script without affecting the main "Run Cycle".
    
def fetch_deep_history(symbol):
    import yfinance as yf
    ticker = f"{symbol}=X"
    print(f"  Downloading {ticker} [Period: 2y]...")
    df = yf.download(ticker, interval="1h", period="2y", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1) 
    df = df.reset_index()
    # Normalize cols
    normalized = []
    for _, row in df.iterrows():
        ts_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
        if pd.isna(row.get(ts_col)): continue
        normalized.append({
            "timestamp": row[ts_col].isoformat(),
            "open": float(row['Open']),
            "high": float(row['High']),
            "low": float(row['Low']),
            "close": float(row['Close']),
            "volume": float(row.get('Volume', 0)),
            "symbol": symbol,
            "atr": np.nan, # prepopulate
            "rsi": np.nan
        })
    # Return last 6000
    if not normalized:
        return pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'symbol'])
        
    df_res = pd.DataFrame(normalized).tail(6000)
    return df_res.reset_index(drop=True)

def run_deep_tournament():
    print("--- Starting Deep Backtest (H1 / 6000 candles / ~1 Year) ---")
    
    champions = [
        {"symbol": "USDJPY", "name": "SMA 10/30 (Aggressive)", "fast_period": 10, "slow_period": 30, "use_rsi_filter": False},
        {"symbol": "USDJPY", "name": "SMA 10/30 + RSI",        "fast_period": 10, "slow_period": 30, "use_rsi_filter": True},
        {"symbol": "GBPUSD", "name": "SMA 20/50 (Balanced)",   "fast_period": 20, "slow_period": 50, "use_rsi_filter": False},
    ]

    import numpy as np # Ensure NP is available

    # Initialize Account for Compounding Test
    # Starting Balance: $10,000
    start_bal = 10000.0
    balance = start_bal
    
    results = []
    
    # Process unique symbols
    unique_symbols = set(c['symbol'] for c in champions)
    data_cache = {}
    
    for sym in unique_symbols:
        df = fetch_deep_history(sym)
        if df.empty:
            print(f"  Warning: No data for {sym}")
            data_cache[sym] = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'symbol', 'atr', 'rsi', 'sma_fast', 'sma_slow'])
            continue

        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        data_cache[sym] = df
        print(f"  Loaded {len(df)} candles for {sym}")

    for cfg in champions:
        sym = cfg['symbol']
        df = data_cache[sym].copy()
        
        print(f"Testing {cfg['name']} on {sym} ({len(df)} candles) WITH COMPOUNDING...")
        
        # We need to act as the "run_single_backtest" but with state
        engine = SignalGenerator("baseline_sma_cross", {k: v for k, v in cfg.items() if k not in ['name', 'symbol']})
        signals = engine.generate(df)
        
        current_balance = start_bal
        wins = 0
        losses = 0
        trades_list = []
        
        for sig in signals:
            # 1. Calculate Size (Risk 2%)
            risk_amt = current_balance * 0.02
            entry = sig['entry_price']
            sl = sig['stop_loss']
            tp = sig['take_profit']
            direction = sig['direction']
            
            dist = abs(entry - sl)
            pip_scalar = 0.01 if "JPY" in sym else 0.0001
            pips = dist / pip_scalar if dist > 0 else 1
            
            # Pip Value approx
            pip_val = 8.0 if "JPY" in sym else 10.0
            
            lots = risk_amt / (pips * pip_val)
            lots = max(0.01, round(lots, 2))
            
            # 2. Simulate Outcome
            entry_idx = df[df['timestamp'] == sig['timestamp']].index[0]
            future = df.iloc[entry_idx+1:]
            
            outcome = None
            pnl_usd = 0
            
            for _, row in future.iterrows():
                if direction == 'LONG':
                    if row['low'] <= sl:
                        outcome = "LOSS"
                        # Loss is roughly the risk amount (slippage aside)
                        pnl_usd = -risk_amt 
                        break
                    elif row['high'] >= tp:
                        outcome = "WIN"
                        # Win is 2x Risk (1:2 ratio)
                        pnl_usd = risk_amt * 2.0
                        break
                elif direction == 'SHORT':
                    if row['high'] >= sl:
                        outcome = "LOSS"
                        pnl_usd = -risk_amt
                        break
                    elif row['low'] <= tp:
                        outcome = "WIN"
                        pnl_usd = risk_amt * 2.0
                        break
            
            if outcome:
                current_balance += pnl_usd
                trades_list.append(outcome)
                if outcome == "WIN": wins += 1
                else: losses += 1
                
        # End of config loop
        total_trades = len(trades_list)
        win_rate = (wins/total_trades*100) if total_trades > 0 else 0
        net_profit_percent = ((current_balance - start_bal) / start_bal) * 100
        
        results.append({
            "Symbol": sym,
            "Strategy": cfg["name"],
            "Trades": total_trades,
            "Win Rate %": round(win_rate, 1),
            "End Balance": round(current_balance, 2),
            "Growth %": round(net_profit_percent, 1)
        })

    # Display Results
    print("\n" + "="*110)
    print(f"{'Symbol':<10} | {'Strategy':<25} | {'Trades':<8} | {'Win Rate':<10} | {'Start $':<10} | {'End $':<12} | {'Growth %':<10}")
    print("-" * 110)
    
    df_res = pd.DataFrame(results)
    if not df_res.empty:
        df_res = df_res.sort_values(by="Growth %", ascending=False)
    
        for _, row in df_res.iterrows():
            print(f"{row['Symbol']:<10} | {row['Strategy']:<25} | {row['Trades']:<8} | {row['Win Rate %']:<10} | {start_bal:<10} | {row['End Balance']:<12} | {row['Growth %']:<10}%")
            
        print("="*110)
        best_res = df_res.iloc[0]
        print(f"\nWINNER (Compound): {best_res['Symbol']} -> ${best_res['End Balance']} (+{best_res['Growth %']}%)")
    else:
        print("No trades generated in deep run.")

if __name__ == "__main__":
    run_deep_tournament()
