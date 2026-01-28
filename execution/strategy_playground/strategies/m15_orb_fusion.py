from backtesting import Strategy
import pandas as pd
import numpy as np
from datetime import time

def EMA(values, n=50):
    return pd.Series(values).ewm(span=n, adjust=False).mean()

def RSI(values, n=14):
    delta = pd.Series(values).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=n).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=n).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def ATR(high, low, close, n=14):
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    tr = pd.concat([(high - low), 
                    (high - close.shift()).abs(), 
                    (low - close.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()

class M15OrbFusionStrategy(Strategy):
    # Session Times (UTC) - Adjust if data is not UTC
    # London Open Candle: 08:00 - 08:15
    london_open_time = time(8, 0)
    
    # NY Open Candle: 13:00 - 13:15 (Winter) / 12:00 (Summer) - keeping simple fixed for now
    ny_open_time = time(13, 0) 
    
    ema_period = 50
    risk_per_trade = 0.02
    rr_ratio = 2.0 # Reward to Risk
    
    def init(self):
        self.ema = self.I(EMA, self.data.Close, self.ema_period)
        self.rsi = self.I(RSI, self.data.Close, 14)
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close, 14)
        
        # State tracking
        self.current_date = None
        self.orb_high = 0
        self.orb_low = 0
        self.orb_active = False # True if we are inside a session watching for breakout
        self.trades_today = 0

    def next(self):
        dt = self.data.index[-1]
        current_time = dt.time()
        today = dt.date()
        
        # Reset daily
        if self.current_date != today:
            self.current_date = today
            self.orb_active = False
            self.trades_today = 0
            
        price = self.data.Close[-1]
        
        # 1. Define Opening Range (First 15m candle of session)
        # Check if current candle is the open candle
        is_london_open = (current_time == self.london_open_time)
        is_ny_open = (current_time == self.ny_open_time)
        
        if is_london_open or is_ny_open:
            # The close of this candle defines the range for the NEXT candles
            # But Backtesting.py 'next' runs AFTER the candle closes.
            # So self.data.High[-1] is the High of the 08:00-08:15 candle.
            self.orb_high = self.data.High[-1]
            self.orb_low = self.data.Low[-1]
            self.orb_active = True
            return # Wait for next candle to break

        # 2. Logic matches only if ORB is active and we haven't traded this session/day overly
        if not self.orb_active: return
        
        # Limit trades per day?
        if self.trades_today >= 2: return
        if self.position: return
        
        # Filters
        ema_val = self.ema[-1]
        rsi_val = self.rsi[-1]
        
        # Trend Filter: Price above EMA = Long Bias
        trend_up = price > ema_val
        trend_down = price < ema_val
        
        # Breakout Logic
        # Long Breakout
        if price > self.orb_high and trend_up:
            if rsi_val < 70: # Not overbought
                self.entry_long(price)
                self.orb_active = False # One trade per session attempt
                self.trades_today += 1
                
        # Short Breakout
        elif price < self.orb_low and trend_down:
            if rsi_val > 30: # Not oversold
                self.entry_short(price)
                self.orb_active = False
                self.trades_today += 1
                
        # Expire ORB if too much time passes? e.g. 2 hours
        # Simple for now: stay active until trade or new session

    def entry_long(self, price):
        # SL below ORB Low or ATR based
        # Using ORB Low + small buffer
        sl = self.orb_low
        dist = price - sl
        
        # Safety check for tiny ranges
        atr = self.atr[-1]
        if dist < (0.5 * atr): 
            sl = price - (1.0 * atr)
            dist = price - sl
            
        tp = price + (dist * self.rr_ratio)
        
        risk_amt = self.equity * self.risk_per_trade
        if dist == 0: return
        size = risk_amt / dist
        
        if size < 1: return
        size = int(round(size))
        
        self.buy(size=size, sl=sl, tp=tp)

    def entry_short(self, price):
        sl = self.orb_high
        dist = sl - price
        
        atr = self.atr[-1]
        if dist < (0.5 * atr):
            sl = price + (1.0 * atr)
            dist = sl - price
            
        tp = price - (dist * self.rr_ratio)
        
        risk_amt = self.equity * self.risk_per_trade
        if dist == 0: return
        size = risk_amt / dist
        
        if size < 1: return
        size = int(round(size))
        
        self.sell(size=size, sl=sl, tp=tp)
