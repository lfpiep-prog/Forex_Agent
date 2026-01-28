from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

# --- Helper Functions ---
def SMA(values, n):
    return pd.Series(values).rolling(n).mean()

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
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def ADX(high, low, close, n=14):
    """
    Average Directional Index (simplified implementation for pandas)
    """
    high = pd.Series(high)
    low = pd.Series(low)
    close = pd.Series(close)
    
    # Needs true range first (ATR)
    tr = ATR(high, low, close, n=1) # 1-period TR for smoothing later
    
    up_move = high - high.shift()
    down_move = low.shift() - low
    
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    
    # Smooth them (Wilder's smoothing is often approx by Exponential Moving Average)
    # Using Rolling Mean for consistency with simple SMA strategy, or simple EMA
    # Standard ADX uses Wilder's Smoothing, but plain EMA is close enough for regime filter
    tr_s = pd.Series(tr).ewm(alpha=1/n, min_periods=n).mean()
    plus_dm_s = pd.Series(plus_dm).ewm(alpha=1/n, min_periods=n).mean()
    minus_dm_s = pd.Series(minus_dm).ewm(alpha=1/n, min_periods=n).mean()
    
    plus_di = 100 * (plus_dm_s / tr_s)
    minus_di = 100 * (minus_dm_s / tr_s)
    
    dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
    adx = dx.ewm(alpha=1/n, min_periods=n).mean()
    
    return adx

# --- Strategy Class ---
class SmaRsiAdxStrategy(Strategy):
    # Trend Params
    sma_fast = 10
    sma_slow = 30
    
    # Regime Filter
    adx_period = 14
    adx_threshold = 25 # Below 25 = Range, Above 25 = Trend
    
    # RSI Params
    rsi_period = 14
    
    # Risk
    sl_atr_mult = 1.5
    tp_atr_mult = 3.0 # Trend TP
    tp_range_mult = 1.0 # Range TP (smaller targets)
    
    risk_per_trade = 0.02

    def init(self):
        # Indicators
        self.sma10 = self.I(SMA, self.data.Close, self.sma_fast)
        self.sma30 = self.I(SMA, self.data.Close, self.sma_slow)
        self.rsi = self.I(RSI, self.data.Close, self.rsi_period)
        self.adx = self.I(ADX, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        self.atr = self.I(ATR, self.data.High, self.data.Low, self.data.Close, 14)

    def next(self):
        if self.position: return
        
        # Check data availability
        if np.isnan(self.adx[-1]) or np.isnan(self.atr[-1]): return

        price = self.data.Close[-1]
        adx_val = self.adx[-1]
        atr_val = self.atr[-1]
        rsi_val = self.rsi[-1]
        
        # --- REGIME: TREND (ADX > Threshold) ---
        if adx_val > self.adx_threshold:
            # Original Trend Following Logic
            if crossover(self.sma10, self.sma30):
                # RSI Filter: Bullish momentum check (50-70)
                if 50 < rsi_val < 70:
                    self.entry_long(price, atr_val, mode="TREND")
            
            elif crossover(self.sma30, self.sma10):
                # RSI Filter: Bearish momentum check (30-50)
                if 30 < rsi_val < 50:
                    self.entry_short(price, atr_val, mode="TREND")
                    
        # --- REGIME: RANGE (ADX < Threshold) ---
        else:
            # Mean Reversion Logic
            # Buy Oversold
            if rsi_val < 30:
                self.entry_long(price, atr_val, mode="RANGE")
            
            # Sell Overbought
            elif rsi_val > 70:
                self.entry_short(price, atr_val, mode="RANGE")

    def entry_long(self, price, atr, mode="TREND"):
        sl_dist = atr * self.sl_atr_mult
        
        # In Range, use tighter TP
        tp_mult = self.tp_range_mult if mode == "RANGE" else self.tp_atr_mult
        tp_dist = atr * tp_mult
        
        sl = price - sl_dist
        tp = price + tp_dist
        
        # Risk Sizing
        risk_amt = self.equity * self.risk_per_trade
        if sl_dist == 0: return
        size = risk_amt / sl_dist
        
        if size < 1: return
        size = int(round(size))
        
        self.buy(size=size, sl=sl, tp=tp)

    def entry_short(self, price, atr, mode="TREND"):
        sl_dist = atr * self.sl_atr_mult
        
        tp_mult = self.tp_range_mult if mode == "RANGE" else self.tp_atr_mult
        tp_dist = atr * tp_mult
        
        sl = price + sl_dist
        tp = price - tp_dist
        
        # Risk Sizing
        risk_amt = self.equity * self.risk_per_trade
        if sl_dist == 0: return
        size = risk_amt / sl_dist
        
        if size < 1: return
        size = int(round(size))
        
        self.sell(size=size, sl=sl, tp=tp)
