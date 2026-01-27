import pandas as pd
import numpy as np
from execution.core.signals import Signal, SignalType

class BaselineSMACross:
    """
    Baseline SMA Crossover Strategy.
    """
    # Configuration Constants
    RSI_PERIOD = 14
    ATR_PERIOD = 14
    
    # Risk Management Constants
    SL_MULTIPLIER = 1.5
    TP_MULTIPLIER = 3.0
    
    # RSI Filter Thresholds
    RSI_OVERBOUGHT = 70
    RSI_BULLISH_MIN = 50
    RSI_OVERSOLD = 30
    RSI_BEARISH_MAX = 50

    def __init__(self, fast_period: int = 50, slow_period: int = 200, use_rsi_filter: bool = False):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.use_rsi_filter = use_rsi_filter

    def calculate(self, df: pd.DataFrame, context: dict = None) -> list[Signal]:
        """
        Calculates signals based on SMA Crossover with optional Sentiment Filter.
        """
        if df.empty:
            return []
            
        sentiment = context.get('sentiment', 'NEUTRAL') if context else 'NEUTRAL'
        
        # 1. Calculate Indicators
        data = self._calculate_indicators(df.copy())
        
        signals = []
        min_periods = max(self.slow_period, 15)
        
        if len(data) < min_periods:
             return []
            
        # Iterate through data to find crossovers
        # maintain previous_row state for crossover detection
        previous_row = data.iloc[self.slow_period - 1]
        
        for i in range(self.slow_period, len(data)):
            current_row = data.iloc[i]
            
            # Skip valid check
            if pd.isna(current_row['atr']) or pd.isna(current_row['rsi']):
                previous_row = current_row
                continue

            # 2. Analyze Candle for Signal
            signal = self._analyze_candle(current_row, previous_row, sentiment)
            if signal:
                signals.append(signal)
            
            previous_row = current_row
            
        return signals

    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds SMA, ATR, and RSI indicators to the DataFrame."""
        # SMAs
        df['sma_fast'] = df['close'].rolling(window=self.fast_period).mean()
        df['sma_slow'] = df['close'].rolling(window=self.slow_period).mean()
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = tr.rolling(window=self.ATR_PERIOD).mean()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.RSI_PERIOD).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df

    def _analyze_candle(self, current: pd.Series, previous: pd.Series, sentiment: str) -> dict | None:
        """Determines if a signal should be generated for the current candle."""
        
        # Detect Crossovers
        bullish_cross = (previous['sma_fast'] <= previous['sma_slow']) and (current['sma_fast'] > current['sma_slow'])
        bearish_cross = (previous['sma_fast'] >= previous['sma_slow']) and (current['sma_fast'] < current['sma_slow'])
        
        if bullish_cross:
            return self._handle_bullish_signal(current, sentiment)
        elif bearish_cross:
            return self._handle_bearish_signal(current, sentiment)
            
        return None

    def _handle_bullish_signal(self, row: pd.Series, sentiment: str) -> dict | None:
        """Validates and creates a LONG signal."""
        # Sentiment Filter
        if sentiment == 'BEARISH':
            return None

        # RSI Filter
        if self.use_rsi_filter:
            if not (self.RSI_BULLISH_MIN < row['rsi'] < self.RSI_OVERBOUGHT):
                return None
                
        # Risk Calc
        atr = row['atr']
        sl_dist = self.SL_MULTIPLIER * atr
        tp_dist = self.TP_MULTIPLIER * atr
        
        return self._create_signal(
            signal_type=SignalType.LONG,
            row=row,
            stop_loss=row['close'] - sl_dist,
            take_profit=row['close'] + tp_dist,
            sentiment=sentiment,
            rationale=f"SMA({self.fast_period}) > SMA({self.slow_period})"
        )

    def _handle_bearish_signal(self, row: pd.Series, sentiment: str) -> dict | None:
        """Validates and creates a SHORT signal."""
        # Sentiment Filter
        if sentiment == 'BULLISH':
            return None

        # RSI Filter
        if self.use_rsi_filter:
            if not (self.RSI_OVERSOLD < row['rsi'] < self.RSI_BEARISH_MAX):
                return None

        # Risk Calc
        atr = row['atr']
        sl_dist = self.SL_MULTIPLIER * atr
        tp_dist = self.TP_MULTIPLIER * atr
        
        return self._create_signal(
            signal_type=SignalType.SHORT,
            row=row,
            stop_loss=row['close'] + sl_dist,
            take_profit=row['close'] - tp_dist,
            sentiment=sentiment,
            rationale=f"SMA({self.fast_period}) < SMA({self.slow_period})"
        )

    def _create_signal(self, signal_type: SignalType, row: pd.Series, stop_loss: float, take_profit: float, sentiment: str, rationale: str) -> Signal:
        """Constructs a typed Signal object."""
        entry_price = row['close']
        rr_ratio = abs(take_profit - entry_price) / abs(entry_price - stop_loss)
        
        full_rationale = (
            f"{rationale} | ATR={row['atr']:.5f} | "
            f"RSI={row['rsi']:.1f} | Sentiment={sentiment} | RR={rr_ratio:.2f}"
        )
        
        return Signal(
            timestamp=row['timestamp'],
            symbol=row['symbol'],
            signal_type=signal_type,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            rationale=full_rationale,
            metadata={'close': entry_price}
        )
