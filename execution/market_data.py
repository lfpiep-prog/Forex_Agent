import pandas as pd
import yfinance as yf
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from execution.config import config

# --- Constants & Types ---

logger = logging.getLogger("MarketData")

class Timeframe:
    H1 = "H1"
    D1 = "D1"
    M15 = "M15"
    M1 = "M1"

class Provider:
    YFINANCE = "yfinance"
    IG = "ig"
    BROKER = "broker" # Alias for IG usually
    TWELVEDATA = "twelvedata"
    POLYGON = "polygon"

class CandleKeys:
    TIMESTAMP = "timestamp"
    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    CLOSE = "close"
    VOLUME = "volume"
    SYMBOL = "symbol"

# Using Dict for now to maintain compatibility with existing pandas conversions
Candle = Dict[str, Any] 

# --- Interface ---

class DataProvider(ABC):
    @abstractmethod
    def fetch_data(self, symbol: str, timeframe: str, limit: int) -> List[Candle]:
        pass

    def _log_fetch(self, source: str, symbol: str, timeframe: str):
        logger.info(f"[{source}] Fetching {symbol} ({timeframe})...")

    def _normalize_timeframe(self, timeframe: str, mapping: Dict[str, str]) -> str:
        return mapping.get(timeframe, mapping.get(Timeframe.H1))

# --- Adapters ---

class YFinanceAdapter(DataProvider):
    """Adapter for yfinance (Free/Public Data)."""
    
    TF_MAP = {
        Timeframe.H1: "1h", 
        Timeframe.D1: "1d", 
        Timeframe.M15: "15m", 
        Timeframe.M1: "1m"
    }

    def fetch_data(self, symbol: str, timeframe: str, limit: int = 100) -> List[Candle]:
        self._log_fetch("YFinance", symbol, timeframe)
        interval = self._normalize_timeframe(timeframe, self.TF_MAP)

        ticker = self._format_ticker(symbol)
        period = self._get_period(limit)

        try:
            df = yf.download(ticker, interval=interval, period=period, progress=False, multi_level_index=False)
        except Exception as e:
            logger.error(f"[YFinance] Error downloading: {e}")
            return []

        if df.empty:
            logger.warning("[YFinance] No data received.")
            return []

        return self._process_dataframe(df, symbol, limit)

    def _format_ticker(self, symbol: str) -> str:
        if len(symbol) == 6 and "=X" not in symbol:
            return f"{symbol}=X"
        return symbol

    def _get_period(self, limit: int) -> str:
        return "2y" if limit > 2000 else "6mo"

    def _process_dataframe(self, df: pd.DataFrame, symbol: str, limit: int) -> List[Candle]:
        df = df.reset_index()
        raw_data = []

        for _, row in df.iterrows():
            ts_col = 'Datetime' if 'Datetime' in df.columns else 'Date'
            if pd.isna(row.get(ts_col)): continue

            raw_data.append({
                CandleKeys.TIMESTAMP: row[ts_col].isoformat(),
                CandleKeys.OPEN: float(row['Open']),
                CandleKeys.HIGH: float(row['High']),
                CandleKeys.LOW: float(row['Low']),
                CandleKeys.CLOSE: float(row['Close']),
                CandleKeys.VOLUME: float(row.get('Volume', 0)),
                CandleKeys.SYMBOL: symbol
            })

        return raw_data[-limit:]


class BrokerAPIAdapter(DataProvider):
    """Adapter for IG Markets."""

    TF_MAP = {
        Timeframe.H1: "1H",
        Timeframe.D1: "1D",
        Timeframe.M15: "15M",
        Timeframe.M1: "1M"
    }

    def fetch_data(self, symbol: str, timeframe: str, limit: int = 100) -> List[Candle]:
        self._log_fetch("BrokerAPI", symbol, timeframe)

        try:
            from execution.brokers.ig_broker import IGBroker
            broker = IGBroker()
            
            if not broker.connect():
                logger.error("[BrokerAPI] Connection failed.")
                return []
            
            resolution = self._normalize_timeframe(timeframe, self.TF_MAP)
            epic = self._get_epic(broker, symbol)
            
            if not epic:
                logger.warning(f"[BrokerAPI] No EPIC found for {symbol}")
                return []

            res = broker.ig_service.fetch_historical_prices_by_epic_and_num_points(
                epic, resolution=resolution, numpoints=limit
            )
            
            return self._process_response(res['prices'], symbol)

        except Exception as e:
            self._handle_error(e)
            return []

    def _get_epic(self, broker, symbol: str) -> Optional[str]:
        epic = broker._find_epic(symbol)
        if not epic and symbol == "USDJPY": 
             return "CS.D.USDJPY.MINI.IP" # Fallback
        return epic

    def _process_response(self, df: pd.DataFrame, symbol: str) -> List[Candle]:
        if df.empty: return []

        # Handle IG's complex columns (bid/ask/last)
        if isinstance(df.columns, pd.MultiIndex):
            df_bid = df['bid'].copy()
        else:
            df_bid = df # Should not happen usually with IG library

        df_bid = df_bid.reset_index()
        raw_data = []

        for _, row in df_bid.iterrows():
            # DateTime is usually the index name or column after reset
            ts = row.get('DateTime') 
            
            raw_data.append({
                CandleKeys.TIMESTAMP: pd.to_datetime(ts).isoformat(),
                CandleKeys.OPEN: float(row['Open']),
                CandleKeys.HIGH: float(row['High']),
                CandleKeys.LOW: float(row['Low']),
                CandleKeys.CLOSE: float(row['Close']),
                CandleKeys.VOLUME: 0.0, # IG Volume is often tick count, better 0 than confusing
                CandleKeys.SYMBOL: symbol
            })
            
        return raw_data

    def _handle_error(self, e: Exception):
        msg = str(e)
        if "exceeded-account-historical-data-allowance" in msg or "403" in msg:
            logger.critical(f"[BrokerAPI] QUOTA EXCEEDED! Switch to 'yfinance'. Error: {e}")
        else:
            logger.error(f"[BrokerAPI] Error fetching data: {e}")


class TwelveDataAdapter(DataProvider):
    """Adapter for Twelve Data."""
    
    TF_MAP = {
        Timeframe.H1: "1h", 
        Timeframe.M1: "1min", 
        Timeframe.M15: "15min", 
        Timeframe.D1: "1day"
    }

    def fetch_data(self, symbol: str, timeframe: str, limit: int = 100) -> List[Candle]:
        self._log_fetch("TwelveData", symbol, timeframe)
        
        try:
            from execution.data_sources.twelvedata_source import TwelveDataSource
            source = TwelveDataSource()
            
            formatted_symbol = self._format_symbol(symbol)
            interval = self._normalize_timeframe(timeframe, self.TF_MAP)
            
            ts = source.client.time_series(
                symbol=formatted_symbol,
                interval=interval,
                outputsize=limit
            )
            df = ts.as_pandas()
            
            if df is None or df.empty:
                logger.warning(f"[TwelveData] No data for {formatted_symbol}.")
                return []
                
            return self._process_dataframe(df, symbol)

        except Exception as e:
            logger.error(f"[TwelveData] Error: {e}")
            return []

    def _format_symbol(self, symbol: str) -> str:
        if "/" not in symbol and "_" not in symbol and len(symbol) == 6:
            return f"{symbol[:3]}/{symbol[3:]}"
        return symbol

    def _process_dataframe(self, df: pd.DataFrame, symbol: str) -> List[Candle]:
        df = df.reset_index()
        raw_data = []
        for _, row in df.iterrows():
            raw_data.append({
                CandleKeys.TIMESTAMP: pd.to_datetime(row['datetime']).isoformat(),
                CandleKeys.OPEN: float(row['open']),
                CandleKeys.HIGH: float(row['high']),
                CandleKeys.LOW: float(row['low']),
                CandleKeys.CLOSE: float(row['close']),
                CandleKeys.VOLUME: float(row.get('volume', 0)),
                CandleKeys.SYMBOL: symbol
            })
        
        raw_data.sort(key=lambda x: x[CandleKeys.TIMESTAMP])
        return raw_data

class PolygonAdapter(DataProvider):
    """Adapter for Polygon.io."""
    
    TF_MAP = {
        Timeframe.H1: ("hour", 1), 
        Timeframe.M1: ("minute", 1), 
        Timeframe.M15: ("minute", 15), 
        Timeframe.D1: ("day", 1)
    }
    
    def fetch_data(self, symbol: str, timeframe: str, limit: int = 100) -> List[Candle]:
        self._log_fetch("Polygon", symbol, timeframe)
        
        try:
            from execution.data_sources.polygon_source import PolygonSource
            source = PolygonSource()
            
            timespan, multiplier = self.TF_MAP.get(timeframe, ("hour", 1))

            end_dt = datetime.utcnow()
            
            # Estimate start time (minutes calculation)
            if timespan == "hour":
                minutes_per_candle = 60 * multiplier
            elif timespan == "day":
                minutes_per_candle = 1440 * multiplier
            else: # minute
                minutes_per_candle = multiplier
            
            total_minutes = limit * minutes_per_candle
            # Buffer for weekends/holidays (x1.6)
            buffer_min = int(total_minutes * 1.6)
            
            start_dt = end_dt - pd.Timedelta(minutes=buffer_min)
            
            # Format YYYY-MM-DD
            s_date = start_dt.strftime("%Y-%m-%d")
            e_date = end_dt.strftime("%Y-%m-%d")
            
            df = source.fetch_candles(symbol, s_date, e_date, timespan=timespan, multiplier=multiplier)
            
            if df.empty:
                logger.warning(f"[Polygon] No data for {symbol}.")
                return []
            
            data = self._process_dataframe(df, symbol)
            return data[-limit:] # Ensure we return only requested amount
            
        except Exception as e:
            logger.error(f"[Polygon] Error: {e}")
            return []

    def _process_dataframe(self, df: pd.DataFrame, symbol: str) -> List[Candle]:
        df = df.reset_index(drop=True)
        raw_data = []
        for _, row in df.iterrows():
            raw_data.append({
                CandleKeys.TIMESTAMP: row['timestamp'].isoformat(),
                CandleKeys.OPEN: float(row['open']),
                CandleKeys.HIGH: float(row['high']),
                CandleKeys.LOW: float(row['low']),
                CandleKeys.CLOSE: float(row['close']),
                CandleKeys.VOLUME: float(row.get('volume', 0)),
                CandleKeys.SYMBOL: symbol
            })
        
        raw_data.sort(key=lambda x: x[CandleKeys.TIMESTAMP])
        return raw_data

class MockDataProvider(DataProvider):
    def fetch_data(self, symbol, timeframe, limit=100):
        logger.warning("[MockProvider] Returning empty mock data.")
        return []

# --- Factory ---

def get_provider() -> DataProvider:
    provider_key = config.DATA_PROVIDER.lower()
    
    providers = {
        Provider.YFINANCE: YFinanceAdapter,
        Provider.IG: BrokerAPIAdapter,
        Provider.BROKER: BrokerAPIAdapter,
        Provider.TWELVEDATA: TwelveDataAdapter,
        Provider.POLYGON: PolygonAdapter
    }
    
    provider_class = providers.get(provider_key, MockDataProvider)
    return provider_class()

# --- Public API ---

def fetch_prices(symbol: str, timeframe: str, limit: int = 100) -> List[Candle]:
    """Public entry point using the configured provider."""
    return get_provider().fetch_data(symbol, timeframe, limit)

def normalize(raw_data: List[Candle]) -> pd.DataFrame:
    """Converts raw list of dicts to a standard Pandas DataFrame."""
    if not raw_data:
        # Return empty DF with expected columns
        cols = [
            CandleKeys.TIMESTAMP, CandleKeys.OPEN, CandleKeys.HIGH, 
            CandleKeys.LOW, CandleKeys.CLOSE, CandleKeys.VOLUME, 
            CandleKeys.SYMBOL, 'atr', 'rsi', 'sma_fast', 'sma_slow'
        ]
        return pd.DataFrame(columns=cols)

    df = pd.DataFrame(raw_data)
    if CandleKeys.TIMESTAMP in df.columns:
        df[CandleKeys.TIMESTAMP] = pd.to_datetime(df[CandleKeys.TIMESTAMP])
    return df
