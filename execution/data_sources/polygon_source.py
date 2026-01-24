import os
import pandas as pd
from datetime import datetime
from polygon import RESTClient
from execution.data_sources.base_source import BaseSource

class PolygonSource(BaseSource):
    def __init__(self):
        self.api_key = os.getenv("POLYGON_API_KEY")
        if not self.api_key:
            raise ValueError("POLYGON_API_KEY not found in environment variables.")
        self.client = RESTClient(self.api_key)

    def fetch_candles(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch aggregated bars (candles) for a forex pair.
        symbol: e.g. "EURUSD" -> "C:EURUSD"
        """
        # Polygon Forex symbols usually prefixed with "C:"
        ticker = f"C:{symbol}" if not symbol.startswith("C:") else symbol
        
        # Determine timeframe - default to 1 minute for "reading candles" capacity
        multiplier = 1
        timespan = "minute"
        
        # Fetch agg v2
        aggs = []
        try:
            for a in self.client.list_aggs(
                ticker, 
                multiplier, 
                timespan, 
                from_=start_date, 
                to=end_date,
                limit=50000
            ):
                aggs.append(a)
        except Exception as e:
            print(f"Error fetching Polygon data for {ticker}: {e}")
            return pd.DataFrame()

        if not aggs:
            return pd.DataFrame()

        # Convert to DataFrame
        data = []
        for a in aggs:
            data.append({
                'timestamp': datetime.fromtimestamp(a.timestamp / 1000),
                'symbol': symbol,  # Store clean symbol "EURUSD"
                'open': a.open,
                'high': a.high,
                'low': a.low,
                'close': a.close,
                'volume': a.volume
            })
            
        df = pd.DataFrame(data)
        
        # Ensure UTC timezone
        if not df.empty:
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
            
        return df
