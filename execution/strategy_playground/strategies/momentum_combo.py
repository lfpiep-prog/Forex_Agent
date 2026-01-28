from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

# --- Indicators ---
def RSI(values, n=14):
    delta = pd.Series(values).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=n).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=n).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def MACD(values, fast=12, slow=26, signal=9):
    fast_ema = pd.Series(values).ewm(span=fast, adjust=False).mean()
    slow_ema = pd.Series(values).ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line

def ATR(high, low, close, n=14):
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(n).mean()

class MomentumComboStrategy(Strategy):
    # Optimizable params
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    rsi_period = 14
    
    rsi_bull_level = 50
    rsi_bear_level = 50
    
    sl_atr = 2.0
    tp_atr = 4.0
    
    risk_per_trade = 0.02

    def init(self):
        self.macd, self.signal = self.I(MACD, self.data.Close, self.macd_fast, self.macd_slow, self.macd_signal)
        self.rsi = self.I(RSI, self.data.Close, self.rsi_period)
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close, 14)

    def next(self):
        if self.position: return
        
        if np.isnan(self.atr[-1]): return

        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        
        # LONG Logic
        # MACD bullish crossover + RSI > 50 (Positive Momentum)
        if crossover(self.macd, self.signal) and self.rsi[-1] > self.rsi_bull_level:
            self.entry_long(price, atr_val)
            
        # SHORT Logic
        # MACD bearish crossover + RSI < 50 (Negative Momentum)
        elif crossover(self.signal, self.macd) and self.rsi[-1] < self.rsi_bear_level:
            self.entry_short(price, atr_val)

    def entry_long(self, price, atr):
        sl = price - (atr * self.sl_atr)
        tp = price + (atr * self.tp_atr)
        
        risk_amt = self.equity * self.risk_per_trade
        sl_dist = price - sl
        if sl_dist == 0: return
        size = risk_amt / sl_dist
        
        if size < 1: return
        size = int(round(size))
        
        self.buy(size=size, sl=sl, tp=tp)

    def entry_short(self, price, atr):
        sl = price + (atr * self.sl_atr)
        tp = price - (atr * self.tp_atr)
        
        risk_amt = self.equity * self.risk_per_trade
        sl_dist = sl - price
        if sl_dist == 0: return
        size = risk_amt / sl_dist
        
        if size < 1: return
        size = int(round(size))
        
        self.sell(size=size, sl=sl, tp=tp)
