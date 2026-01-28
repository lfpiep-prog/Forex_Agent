
import sys
import os
import pandas as pd
from datetime import datetime

# Add execution path to find modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from execution.config import config
from execution.market_data import fetch_prices

def test_polygon():
    print(f"Current Config DATA_PROVIDER: {config.DATA_PROVIDER}")
    print(f"Polygon API Key Present: {bool(os.getenv('POLYGON_API_KEY'))}")
    
    if config.DATA_PROVIDER != "polygon":
        print("WARNING: Config is not set to 'polygon'. Initializing force...")
        # Since config is loaded at import, we might need to rely on env var causing it, 
        # but we already updated .env and file.
        pass

    print(f"\n--- Testing Permissions ---")
    
    symbol = "EURUSD"
    timeframes = ["D1", "M1", "H1"]
    
    for tf in timeframes:
        print(f"\nTesting {tf}...")
        try:
            data = fetch_prices(symbol, tf, limit=5)
            if data:
                print(f"SUCCESS: {tf} returned {len(data)} candles.")
            else:
                print(f"FAILURE: {tf} returned empty.")
        except Exception as e:
            print(f"EXCEPTION {tf}: {e}")

if __name__ == "__main__":
    test_polygon()
