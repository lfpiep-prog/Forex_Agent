
import logging
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

logger = logging.getLogger("YFinanceProvider")

class YFinanceDataProvider:
    def __init__(self):
        logger.info("Initialized YFinance Data Provider")
        
    def fetch_latest_candles(self, symbol: str, period="1d", interval="1m") -> pd.DataFrame:
        """
        Fetches latest candles from Yahoo Finance.
        
        Args:
            symbol (str): e.g. "EURUSD=X" (Yahoo format) or "EUR_USD" (our format)
            period (str): "1d", "5d", "1mo"
            interval (str): "1m", "5m", "1h"
            
        Returns:
            pd.DataFrame: DataFrame with [timestamp, open, high, low, close, volume]
        """
        # Map generic symbol to Yahoo Symbol if needed
        # We assume our system uses 'EUR_USD', Yahoo uses 'EURUSD=X'
        yahoo_symbol = symbol.replace("_", "") + "=X"
        
        logger.info(f"Fetching {period} data for {yahoo_symbol} interval={interval}...")
        
        try:
            ticker = yf.Ticker(yahoo_symbol)
            # Fetch data
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"No data returned for {yahoo_symbol}")
                return pd.DataFrame()
            
            # Normalize Columns
            # Yahoo returns: Index=Datetime, Open, High, Low, Close, Volume, Dividends, Stock Splits
            df.reset_index(inplace=True)
            
            # Rename for compatibility
            df.rename(columns={
                "Datetime": "timestamp",
                "Date": "timestamp", # Sometimes returns 'Date' if interval is daily
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume"
            }, inplace=True)
            
            df['symbol'] = symbol
            
            # Ensure timestamp is UTC and clean timezone info for simpler processing if needed, 
            # but usually it's timezone-aware. Let's keep it aware.
            
            # Select only needed columns
            df = df[['timestamp', 'symbol', 'open', 'high', 'low', 'close']]
            
            logger.info(f"Fetched {len(df)} candles. Last Close: {df.iloc[-1]['close']:.5f} @ {df.iloc[-1]['timestamp']}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching YFinance data: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    p = YFinanceDataProvider()
    d = p.fetch_latest_candles("EUR_USD")
    print(d.tail())
