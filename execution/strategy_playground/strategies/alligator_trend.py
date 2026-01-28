from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

# --- Indicators ---
def Alligator(values, jaw_p=13, jaw_s=8, teeth_p=8, teeth_s=5, lips_p=5, lips_s=3):
    # SMMA (Smoothed Moving Average) approx via EWM/Rolling
    # Alligator uses Median Price (High+Low)/2
    # For simplicity here using Close or HL2 if passed
    # Assuming values is Close for basic implementation, or we pass median
    
    # Williams SMMA is specific. Simplified here:
    # Jaw (Blue): 13-period SMMA, shifted 8 bars forward
    # Teeth (Red): 8-period SMMA, shifted 5 bars forward
    # Lips (Green): 5-period SMMA, shifted 3 bars forward
    
    def smma(series, n):
        return series.ewm(alpha=1/n, adjust=False).mean()

    s = pd.Series(values)
    jaw = smma(s, jaw_p).shift(jaw_s)
    teeth = smma(s, teeth_p).shift(teeth_s)
    lips = smma(s, lips_p).shift(lips_s)
    
    return jaw, teeth, lips

def MACD(values, fast=12, slow=26, signal=9):
    fast_ema = pd.Series(values).ewm(span=fast, adjust=False).mean()
    slow_ema = pd.Series(values).ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line

class AlligatorTrendStrategy(Strategy):
    risk_per_trade = 0.02
    
    def init(self):
        # Calculate Median Price
        self.median_price = (self.data.High + self.data.Low) / 2
        
        self.jaw, self.teeth, self.lips = self.I(Alligator, self.data.Close, 13, 8, 8, 5, 5, 3)
        self.macd, self.signal = self.I(MACD, self.data.Close, 12, 26, 9)

    def next(self):
        price = self.data.Close[-1]
        
        # Helper variables
        jaw = self.jaw[-1]
        teeth = self.teeth[-1]
        lips = self.lips[-1]
        
        if np.isnan(jaw): return

        # Exit Logic: Lips crossing back into Teeth/Jaw (Trend Weakening)
        if self.position.is_long:
            if lips < teeth: # Green crosses below Red
                self.position.close()
                
        elif self.position.is_short:
            if lips > teeth: # Green crosses above Red
                self.position.close()

        # Entry Logic
        if not self.position:
            # LONG: Lips > Teeth > Jaw (Eating Mode) AND MACD Bullish
            if (lips > teeth > jaw) and (self.macd[-1] > self.signal[-1]):
                self.entry_long(price)
                
            # SHORT: Lips < Teeth < Jaw (Eating Mode Down) AND MACD Bearish
            elif (lips < teeth < jaw) and (self.macd[-1] < self.signal[-1]):
                self.entry_short(price)

    def entry_long(self, price):
        # ATR based SL or just Fixed %? Using simplistic SL for Alligator usually trailing
        # Using a wide fixed SL for safety
        sl = price * 0.99 
        
        risk_amt = self.equity * self.risk_per_trade
        sl_dist = price - sl
        size = risk_amt / sl_dist
        
        if size < 1: return
        size = int(round(size))
        
        self.buy(size=size, sl=sl)

    def entry_short(self, price):
        sl = price * 1.01
        
        risk_amt = self.equity * self.risk_per_trade
        sl_dist = sl - price
        size = risk_amt / sl_dist
        
        if size < 1: return
        size = int(round(size))
        
        self.sell(size=size, sl=sl)
