
import sys
import os
import pandas as pd
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv()

from execution.brokers.ig_broker import IGBroker

def test_history():
    print("--- Testing IG Historical Data Fetch ---")
    broker = IGBroker()
    if not broker.connect():
        print("Failed to connect")
        return

    symbol = "USDJPY"
    # Get EPIC from internal helper
    epic = broker._find_epic(symbol) 
    if not epic:
        print(f"No EPIC found for {symbol}")
        # manual fallback for testing if config logic fails
        epic = "CS.D.USDJPY.MINI.IP" 
    
    print(f"Fetching 10 candles for {epic}...")
    
    # 1H resolution = '1H' ? in IG it might be 'HOUR'
    # resolution: 'MINUTE', 'MINUTE_2', 'MINUTE_3', 'MINUTE_5', 'MINUTE_10', 'MINUTE_15', 'MINUTE_30', 'HOUR', 'HOUR_2', 'HOUR_3', 'HOUR_4', 'DAY', 'WEEK', 'MONTH'
    
    try:
        # fetch_historical_prices_by_epic_and_num_points
        # Valid resolutions: MINUTE, MINUTE_2, MINUTE_3, MINUTE_5, MINUTE_10, MINUTE_15, MINUTE_30, HOUR, HOUR_2, HOUR_3, HOUR_4, DAY, WEEK, MONTH
        res = broker.ig_service.fetch_historical_prices_by_epic_and_num_points(
            epic, 
            resolution='1H', 
            numpoints=10
        )
        
        # Returns: (prices: pandas.DataFrame, metadata: dict)
        prices_df = res['prices']
        print(f"Received {len(prices_df)} rows")
        print(prices_df.head())
        print(prices_df.columns)
        
    except Exception as e:
        print(f"Error fetching history: {e}")

if __name__ == "__main__":
    test_history()
