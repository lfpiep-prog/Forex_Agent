import os
import sys
import pandas as pd
from dotenv import load_dotenv
from execution.data_sources.twelvedata_source import TwelveDataSource

# Load environment variables
load_dotenv()

def run_test():
    print("--- Verifying USDJPY on Twelve Data ---")
    
    source = TwelveDataSource()
    symbol = "USDJPY"
    start = "2024-11-20" 
    end = "2024-11-22"
    
    print(f"Fetching {symbol} for {start} to {end}...")
    try:
        df = source.fetch_candles(symbol, start, end)
        
        if df.empty:
            print("WARNING: Result is empty.")
        else:
            print(f"SUCCESS: Retrieved {len(df)} rows for {symbol}.")
            print(df.head(1))
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    run_test()
