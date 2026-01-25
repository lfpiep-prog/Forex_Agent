from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
from execution.models import OrderIntent, OrderResult
from pandas import DataFrame

class IBroker(ABC):
    """
    Interface for Broker implementations (IG, Oanda, Mock, etc.)
    """
    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def get_balance(self) -> Optional[Dict[str, float]]:
        """Returns {balance, equity, available} or None if failed"""
        pass

    @abstractmethod
    def execute_order(self, order_intent: OrderIntent) -> OrderResult:
        pass


class IDataSource(ABC):
    """
    Interface for Market Data Providers (TwelveData, Yahoo, etc.)
    """
    @abstractmethod
    def get_latest_price(self, symbol: str) -> Optional[float]:
        pass

    @abstractmethod
    def get_historical_data(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[DataFrame]:
        pass


class IStrategy(ABC):
    """
    Interface for Trading Strategies
    """
    @abstractmethod
    def analyze(self, market_data: DataFrame) -> Dict[str, Any]:
        """
        Analyzes data and returns a signal/result dict.
        """
        pass
