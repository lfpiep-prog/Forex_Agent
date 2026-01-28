from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

# --- Indicators ---
def BollingerBands(values, n=20, std_dev=2):
    sma = pd.Series(values).rolling(n).mean()
    std = pd.Series(values).rolling(n).std()
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    return upper, lower

def ATR(high, low, close, n=14):
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    tr = pd.concat([(high - low), 
                    (high - close.shift()).abs(), 
                    (low - close.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()

class BollingerBreakoutStrategy(Strategy):
    bb_period = 20
    bb_dev = 2.0
    
    sl_atr = 1.0 # Tighter SL
    risk_per_trade = 0.02

    def init(self):
        self.upper, self.lower = self.I(BollingerBands, self.data.Close, self.bb_period, self.bb_dev)
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close, 14)

    def next(self):
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        
        if np.isnan(atr_val): return

        # Exit logic first: Close positions if price reverts back inside bands
        if self.position.is_long and price < self.upper[-1]:
            self.position.close()
        elif self.position.is_short and price > self.lower[-1]:
            self.position.close()

        # Entry logic: Breakout
        if not self.position:
            # Long Breakout
            if price > self.upper[-1]:
                self.entry_long(price, atr_val)
            
            # Short Breakout
            elif price < self.lower[-1]:
                self.entry_short(price, atr_val)

    def entry_long(self, price, atr):
        sl = price - (atr * self.sl_atr)
        
        risk_amt = self.equity * self.risk_per_trade
        sl_dist = price - sl
        if sl_dist == 0: return
        size = risk_amt / sl_dist
        
        if size < 1: return
        size = int(round(size))
        
        # No TP, ride the trend until close back inside band
        self.buy(size=size, sl=sl)

    def entry_short(self, price, atr):
        sl = price + (atr * self.sl_atr)
        
        risk_amt = self.equity * self.risk_per_trade
        sl_dist = sl - price
        if sl_dist == 0: return
        size = risk_amt / sl_dist
        
        if size < 1: return
        size = int(round(size))
        
        self.sell(size=size, sl=sl)
