from backtesting import Strategy
import pandas as pd
import numpy as np
from datetime import time

class LondonBreakoutStrategy(Strategy):
    # Parameters (UTC times assumes data is UTC)
    # Asian Session: 00:00 - 08:00 UTC (Adjust if data is different timezone)
    asia_start = time(0, 0)
    asia_end = time(8, 0)
    
    # Trading Session: 08:00 - 18:00 UTC
    trade_start = time(8, 0)
    trade_end = time(18, 0)
    
    # Risk
    risk_per_trade = 0.02
    sl_pips = 30 # Fixed SL for simplicity or Range based
    
    def init(self):
        # We need to track the High/Low of the Asian session each day
        self.asia_high = 0
        self.asia_low = 999999
        self.current_date = None
        self.entry_triggered = False

    def next(self):
        # Function to handle day change
        dt = self.data.index[-1]
        current_time = dt.time()
        today = dt.date()
        
        # Reset on new day
        if self.current_date != today:
            self.current_date = today
            self.asia_high = 0
            self.asia_low = 999999
            self.entry_triggered = False # Can trade once per day

        price = self.data.Close[-1]
        
        # 1. Asian Session: Record High/Low
        if self.asia_start <= current_time < self.asia_end:
            if price > self.asia_high: self.asia_high = price
            if price < self.asia_low: self.asia_low = price
            
        # 2. Trading Session: Check for Breakout
        elif self.trade_start <= current_time < self.trade_end:
            if self.position: 
                return # Already in a trade
                
            if self.entry_triggered:
                return # Already took a trade today
            
            # Sanity check for valid range
            if self.asia_high == 0 or self.asia_low == 999999:
                return

            # Long Breakout
            if price > self.asia_high:
                self.entry_long(price)
                self.entry_triggered = True
                
            # Short Breakout
            elif price < self.asia_low:
                self.entry_short(price)
                self.entry_triggered = True
        
        # 3. End of Day: Close Logic (optional, or let SL/TP hit)
        # Here we just hold, or close at trade_end?
        # Let's close at end of session to avoid overnight risk if strictly intraday
        if current_time >= self.trade_end and self.position:
            self.position.close()

    def entry_long(self, price):
        # Stop loss: either fixed pips or below Asia Low
        # Let's use Asia Low as SL for true structure
        sl = self.asia_low
        tp_dist = (price - sl) * 1.5 # 1.5R 
        tp = price + tp_dist
        
        risk_amt = self.equity * self.risk_per_trade
        sl_dist = price - sl
        
        if sl_dist <= 0: return # Error
        
        size = risk_amt / sl_dist
        if size < 1: return
        size = int(round(size))
        
        self.buy(size=size, sl=sl, tp=tp)

    def entry_short(self, price):
        sl = self.asia_high
        tp_dist = (sl - price) * 1.5
        tp = price - tp_dist
        
        risk_amt = self.equity * self.risk_per_trade
        sl_dist = sl - price
        
        if sl_dist <= 0: return
        
        size = risk_amt / sl_dist
        if size < 1: return
        size = int(round(size))
        
        self.sell(size=size, sl=sl, tp=tp)
