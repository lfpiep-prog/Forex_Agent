from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

def SMA(values, n):
    """
    Return simple moving average of `values`, at
    each step taking into account `n` previous values.
    """
    return pd.Series(values).rolling(n).mean()

def RSI(values, n=14):
    """
    Relative Strength Index
    """
    delta = pd.Series(values).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=n).mean() # Simplified rolling mean RSI for speed/stability
    loss = (-delta.where(delta < 0, 0)).rolling(window=n).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def ATR(high, low, close, n=14):
    """
    Average True Range
    """
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(n).mean()
    return atr

class SmaRsiAtrStrategy(Strategy):
    # Parameters
    sma_fast = 10
    sma_slow = 30
    rsi_period = 14
    atr_period = 14
    
    rsi_long_min = 50
    rsi_long_max = 70
    rsi_short_min = 30
    rsi_short_max = 50
    
    sl_atr_mult = 1.5
    tp_atr_mult = 3.0
    risk_per_trade = 0.02 # 2%

    def init(self):
        # Indicators
        self.sma10 = self.I(SMA, self.data.Close, self.sma_fast)
        self.sma30 = self.I(SMA, self.data.Close, self.sma_slow)
        self.rsi = self.I(RSI, self.data.Close, self.rsi_period)
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        
        # Skip if ATR is NaN (early data)
        if np.isnan(atr_val) or atr_val == 0:
            return

        # Check for open trades to avoid duplicate entries (simplified)
        if self.position:
            return

        # LONG Logic
        # LONG Logic
        if crossover(self.sma10, self.sma30):
            # RSI Filter: 50 < RSI < 70
            if self.rsi_long_min < self.rsi[-1] < self.rsi_long_max:
                self.entry_long(price, atr_val)

        # SHORT Logic
        elif crossover(self.sma30, self.sma10):
            # RSI Filter: 30 < RSI < 50
            if self.rsi_short_min < self.rsi[-1] < self.rsi_short_max:
                self.entry_short(price, atr_val)
    
    def entry_long(self, price, atr):
        sl_dist = atr * self.sl_atr_mult
        tp_dist = atr * self.tp_atr_mult
        
        sl_price = price - sl_dist
        tp_price = price + tp_dist
        
        # Calculate size based on risk
        risk_amt = self.equity * self.risk_per_trade
        # Risk = Size * (Entry - SL) -> Size = Risk / (Entry - SL)
        size = risk_amt / sl_dist
        
        # Determine strict integer size (or fraction if supported, backtesting.py usually supports fractions but specific to asset)
        # Using a safeguard for min size
        if size < 1: 
             return # Too small to trade
        
        size = int(round(size))
        
        self.buy(size=size, sl=sl_price, tp=tp_price)

    def entry_short(self, price, atr):
        sl_dist = atr * self.sl_atr_mult
        tp_dist = atr * self.tp_atr_mult
        
        sl_price = price + sl_dist
        tp_price = price - tp_dist
        
        # Calculate size based on risk
        risk_amt = self.equity * self.risk_per_trade
        size = risk_amt / sl_dist
        
        if size < 1: 
             return

        size = int(round(size))

        self.sell(size=size, sl=sl_price, tp=tp_price)
