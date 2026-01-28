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
    # Optimizable Parameters
    jaw_p = 13
    jaw_s = 8
    teeth_p = 8
    teeth_s = 5
    lips_p = 5
    lips_s = 3
    
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    
    # Filter
    use_adx_filter = True
    adx_period = 14
    adx_threshold = 20 # Optimized for 2025 Regime
    
    # Risk Management
    sl_atr_mult = 3.0   # Optimized (Wide)
    tp_atr_mult = 5.0   # Placeholder
    use_trailing_sl = True 
    risk_per_trade = 0.02 # 2% Compounding Risk
    margin = 0.02 # 50:1 Leverage
    
    # Internal state for sizing
    # calculated at entry based on current equity
    
    def init(self):
        # ... indicators ...
        self.jaw, self.teeth, self.lips = self.I(Alligator, self.data.Close, 
                                                 self.jaw_p, self.jaw_s, 
                                                 self.teeth_p, self.teeth_s, 
                                                 self.lips_p, self.lips_s)
                                                 
        self.macd, self.signal = self.I(MACD, self.data.Close, 
                                        self.macd_fast, self.macd_slow, self.macd_signal)
                                        
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close, 14)
        
        # ADX
        if self.use_adx_filter:
            self.adx = self.I(ADX, self.data.High, self.data.Low, self.data.Close, self.adx_period)
            
        # Manual SL Tracking (reset on init only)
        self.manual_sl = 0

    def next(self):
        # 0. Check Manual SL Hit (simulating intrabar)
        price = self.data.Close[-1]
        high = self.data.High[-1]
        low = self.data.Low[-1]
        
        # Helper variables
        jaw = self.jaw[-1]
        teeth = self.teeth[-1]
        lips = self.lips[-1]
        atr = self.atr[-1]
        
        if np.isnan(jaw) or np.isnan(atr): return
        
        # Manage Trailing Stop
        if self.position:
            if self.position.is_long:
                # Check exit
                if self.use_trailing_sl and low <= self.manual_sl:
                    self.position.close()
                    return
                
                # Update Trail
                if self.use_trailing_sl:
                    new_sl = price - (atr * self.sl_atr_mult)
                    if new_sl > self.manual_sl:
                        self.manual_sl = new_sl
                        
            elif self.position.is_short:
                # Check exit
                if self.use_trailing_sl and high >= self.manual_sl:
                    self.position.close()
                    return
                
                # Update Trail
                if self.use_trailing_sl:
                    new_sl = price + (atr * self.sl_atr_mult)
                    if new_sl < self.manual_sl or self.manual_sl == 0:
                        self.manual_sl = new_sl

        # Entry Logic
        if not self.position:
            # Check Filters
            filter_ok = True
            if self.use_adx_filter:
                if self.adx[-1] < self.adx_threshold:
                    filter_ok = False
            
            if not filter_ok: return

            # LONG
            if (lips > teeth > jaw) and (self.macd[-1] > self.signal[-1]):
                self.entry_long(price, atr)
                
            # SHORT
            elif (lips < teeth < jaw) and (self.macd[-1] < self.signal[-1]):
                self.entry_short(price, atr)

    def entry_long(self, price, atr):
        sl_dist = atr * self.sl_atr_mult
        sl = price - sl_dist
        
        # Risk Calc
        risk_amt = self.equity * self.risk_per_trade
        if sl_dist == 0: return
        size = risk_amt / sl_dist
        
        # Margin Cap (Leverage 50:1 assumed roughly)
        if self.margin > 0:
            max_size = (self.equity * 0.95) / (price * self.margin)
            size = min(size, max_size)
        
        if size < 1: return
        size = int(round(size))
        
        # Initialize Manual SL
        if self.use_trailing_sl:
            self.manual_sl = sl
            tp = None
            self.buy(size=size) 
        else:
             tp = price + (atr * self.tp_atr_mult)
             self.buy(size=size, sl=sl, tp=tp)

    def entry_short(self, price, atr):
        sl_dist = atr * self.sl_atr_mult
        sl = price + sl_dist
        
        # Risk Calc
        risk_amt = self.equity * self.risk_per_trade
        if sl_dist == 0: return
        size = risk_amt / sl_dist
        
        # Margin Cap
        if self.margin > 0:
            max_size = (self.equity * 0.95) / (price * self.margin)
            size = min(size, max_size)
        
        if size < 1: return
        size = int(round(size))
        
        # Initialize Manual SL
        if self.use_trailing_sl:
            self.manual_sl = sl
            tp = None
            self.sell(size=size)
        else:
             tp = price - (atr * self.tp_atr_mult)
             self.sell(size=size, sl=sl, tp=tp)

def ADX(high, low, close, n=14):
    # Standard ADX implementation
    # Calculating Directional Movement
    # Using pandas ewm for smoothing
    
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    
    up = high - high.shift(1)
    down = low.shift(1) - low
    
    pos_dm = np.where((up > down) & (up > 0), up, 0.0)
    neg_dm = np.where((down > up) & (down > 0), down, 0.0)
    
    tr = ATR(high, low, close, 1) # True Range 1-period
    
    # Smooth
    # ADX uses Wilders Smoothing which is alpha=1/n
    alpha = 1/n
    
    def smooth(series, n):
        return pd.Series(series).ewm(alpha=1/n, adjust=False).mean()
        
    s_tr = smooth(tr, n)
    s_pos_dm = smooth(pos_dm, n)
    s_neg_dm = smooth(neg_dm, n)
    
    pos_di = 100 * (s_pos_dm / s_tr)
    neg_di = 100 * (s_neg_dm / s_tr)
    
    dx = 100 * abs(pos_di - neg_di) / (pos_di + neg_di)
    adx = smooth(dx, n)
    
    return adx.to_numpy()

def ATR(high, low, close, n=14):
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    tr = pd.concat([(high - low), 
                    (high - close.shift()).abs(), 
                    (low - close.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean().to_numpy()
