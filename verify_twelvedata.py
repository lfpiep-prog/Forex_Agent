import os
import sys
import pandas as pd
from dotenv import load_dotenv
from execution.data_sources.twelvedata_source import TwelveDataSource

# Load environment variables
load_dotenv()

def run_test():
    print("--- Verifying Twelve Data Connection ---")
    
    # Check for API Key
    key = os.getenv("TWELVEDATA_API_KEY")
    if not key:
        print("ERROR: TWELVEDATA_API_KEY not set in environment.")
        return

    print(f"API Key present: {key[:4]}...{key[-4:]}")
    
    source = TwelveDataSource()
    symbol = "EURUSD"
    # Twelve Data Free Plan limits historical depth significantly (e.g. 5000 points).
    # Using a known trading week in late 2024 to avoid holidays.
    start = "2024-11-20" 
    end = "2024-11-22"
    
    print(f"Fetching {symbol} for {start} to {end}...")
    try:
        df = source.fetch_candles(symbol, start, end)
        
        if df.empty:
            print("WARNING: Result is empty. Check internet or API limit.")
        else:
            print(f"SUCCESS: Retrieved {len(df)} rows.")
            print(df.head())
            
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")

if __name__ == "__main__":
    # Ensure project root is in path
    sys.path.append(os.getcwd())
    run_test()
