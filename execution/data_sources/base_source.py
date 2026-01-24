from abc import ABC, abstractmethod
import pandas as pd

class BaseSource(ABC):
    """
    Abstract base class for all data providers.
    """
    
    @abstractmethod
    def fetch_candles(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch historical candles for a given symbol and date range.
        Must return a DataFrame with columns: [timestamp, open, high, low, close, volume]
        """
        pass
