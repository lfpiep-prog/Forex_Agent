import os
import pandas as pd
from twelvedata import TDClient
import datetime
from execution.data_sources.base_source import BaseSource

class TwelveDataSource(BaseSource):
    def __init__(self):
        self.api_key = os.getenv("TWELVEDATA_API_KEY")
        if not self.api_key:
            raise ValueError("TWELVEDATA_API_KEY not found in environment variables.")
        self.client = TDClient(apikey=self.api_key)

    def fetch_candles(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch candles from Twelve Data.
        symbol: e.g. "EURUSD". Twelve Data uses "EUR/USD".
        """
        # Symbol Translation: EURUSD -> EUR/USD
        if "/" not in symbol and "_" not in symbol:
             # Assume standard 6 char forex pair
             formatted_symbol = f"{symbol[:3]}/{symbol[3:]}"
        else:
             formatted_symbol = symbol.replace("_", "/")
        
        # Interval: 1min is best for high capacity reading
        try:
            # Twelvedata time_series returns a TimeSeries object
            # outputsize is limit. Free tier is 800 credits/day, but batch size counts as 1 credit usually?
            # Or huge requests might be paginated. 
            # We use 5000 as a safe batch size.
            ts = self.client.time_series(
                symbol=formatted_symbol,
                interval="1min",
                start_date=start_date,
                end_date=end_date,
                outputsize=5000 
            )
            df = ts.as_pandas()
            
        except Exception as e:
            print(f"Error fetching TwelveData for {formatted_symbol}: {e}")
            return pd.DataFrame()

        if df is None or df.empty:
            return pd.DataFrame()

        # DataFrame comes with index as datetime, and cols: open, high, low, close.
        # Ensure format matches our system: [timestamp, symbol, open, high, low, close, volume]
        
        # Reset index to get timestamp as column
        df = df.reset_index()
        df.rename(columns={'datetime': 'timestamp'}, inplace=True)
        
        # Add symbol column
        df['symbol'] = symbol # use internal format 'EURUSD'
        
        # Ensure types (they usually come as float, but just in case)
        cols = ['open', 'high', 'low', 'close']
        for c in cols:
            df[c] = pd.to_numeric(df[c])
            
        # Volume might be missing for Forex
        if 'volume' not in df.columns:
            df['volume'] = 0
            
        # Ensure UTC
        # TwelveData usually returns local time or ET? default is UTC usually or exchange time.
        # For Forex it's usually UTC.
        if 'timestamp' in df.columns:
             try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                # If naive, assume UTC
                if df['timestamp'].dt.tz is None:
                    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC')
                else:
                    df['timestamp'] = df['timestamp'].dt.tz_convert('UTC')
             except Exception:
                 pass

        return df
