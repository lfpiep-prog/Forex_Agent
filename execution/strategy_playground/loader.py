import pandas as pd
import os
from execution.data_sources.polygon_source import PolygonSource

def load_data(symbol: str, start_date: str, end_date: str, timeframe: str = "minute", multiplier: int = 60) -> pd.DataFrame:
    """
    Load data from Polygon and format it for backtesting.py.
    
    Args:
        symbol (str): The forex symbol (e.g., "EURUSD").
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        timeframe (str): Timeframe for Polygon (e.g., 'minute', 'hour', 'day').
        multiplier (int): Multiplier for the timeframe (default 60 for 1H if timeframe is minute, or use 'hour' and 1).
    
    Returns:
        pd.DataFrame: Dataframe with index as Datetime and columns Open, High, Low, Close, Volume.
    """
    source = PolygonSource()
    
    # Fetch data using existing PolygonSource
    # Note: PolygonSource.fetch_candles returns lower case columns: open, high, low, close, volume, timestamp
    df = source.fetch_candles(symbol, start_date, end_date, timespan=timeframe, multiplier=multiplier)
    
    if df.empty:
        print(f"No data found for {symbol}")
        return pd.DataFrame()

    # Rename columns to match Backtesting.py requirements (Capitalized)
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })

    # Set timestamp as index
    if 'timestamp' in df.columns:
        df = df.set_index('timestamp')
    
    # Ensure index is datetime
    df.index = pd.to_datetime(df.index)
    
    # Drop any other columns if necessary, but keeping them is usually fine.
    return df
