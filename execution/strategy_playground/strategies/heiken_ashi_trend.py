from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

# --- Indicators ---
def HeikenAshi(open_p, high, low, close):
    # backtesting.py passes numpy arrays, not pandas Series
    ha_close = (open_p + high + low + close) / 4
    
    ha_open = np.zeros_like(open_p)
    ha_open[0] = open_p[0]
    
    for i in range(1, len(open_p)):
        ha_open[i] = (ha_open[i-1] + ha_close[i-1]) / 2
        
    return ha_open, ha_close

def EMA(values, n=50):
    return pd.Series(values).ewm(span=n, adjust=False).mean()

def ATR(high, low, close, n=14):
    # Convert manually to series for rolling calc or use talib if available
    # Simple manual pandas implementation
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    tr = pd.concat([(high - low), 
                    (high - close.shift()).abs(), 
                    (low - close.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean().to_numpy() # Return numpy array

class HeikenAshiTrendStrategy(Strategy):
    ema_period = 200 # Trend Filter
    risk_per_trade = 0.02
    
    def init(self):
        # Calculate HA
        self.ha_open, self.ha_close = self.I(HeikenAshi, self.data.Open, self.data.High, self.data.Low, self.data.Close)
        self.ema = self.I(EMA, self.data.Close, self.ema_period)
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close, 14)

    def next(self):
        if len(self.ha_close) < 5: return
        
        current_ha_close = self.ha_close[-1]
        current_ha_open = self.ha_open[-1]
        prev_ha_close = self.ha_close[-2]
        prev_ha_open = self.ha_open[-2]
        
        price = self.data.Close[-1]
        ema_val = self.ema[-1]
        atr = self.atr[-1]
        if np.isnan(atr): return
        
        # Determine Color
        is_green = current_ha_close > current_ha_open
        was_green = prev_ha_close > prev_ha_open
        is_red = current_ha_close < current_ha_open
        was_red = prev_ha_close < prev_ha_open
        
        # Exit Logic: Color Flip
        if self.position.is_long and is_red:
            self.position.close()
        elif self.position.is_short and is_green:
            self.position.close()
            
        # Entry Logic
        if not self.position:
            # LONG: Color Flip Red->Green AND Price > EMA 200 (Uptrend)
            if is_green and was_red and (price > ema_val):
                self.entry_long(price, atr)
            
            # SHORT: Color Flip Green->Red AND Price < EMA 200 (Downtrend)
            elif is_red and was_green and (price < ema_val):
                self.entry_short(price, atr)

    def entry_long(self, price, atr):
        # SL below recent swing or simpler: 2x ATR
        sl = price - (atr * 2.0)
        
        risk_amt = self.equity * self.risk_per_trade
        sl_dist = price - sl
        if sl_dist == 0: return
        size = risk_amt / sl_dist
        
        if size < 1: return
        size = int(round(size))
        
        # No TP, Ride trend until color flip
        self.buy(size=size, sl=sl)

    def entry_short(self, price, atr):
        sl = price + (atr * 2.0)
        
        risk_amt = self.equity * self.risk_per_trade
        sl_dist = sl - price
        if sl_dist == 0: return
        size = risk_amt / sl_dist
        
        if size < 1: return
        size = int(round(size))
        
        self.sell(size=size, sl=sl)
