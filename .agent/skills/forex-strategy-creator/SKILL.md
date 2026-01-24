---
name: forex-strategy-creator
description: Workflow for generating 1H candle strategies, selecting pairs, and performing initial backtests.
---

# Forex Strategy Creator

**Goal**: Systematically create and backtest simple trading strategies on 1H candles across various currency pairs.

## Workflow

1.  **Idea Generation**
    -   Start simple: Trend Following (SMA/EMA), Mean Reversion (RSI/Bollinger), or Breakout.
    -   Define Entry Rule (e.g., `Close > SMA200`).
    -   Define Exit Rule (e.g., `Close < SMA200` or TakeProfit/StopLoss).

2.  **Pair Selection**
    -   Test on Majors first: EURUSD, GBPUSD, USDJPY.
    -   Test on Crosses second: EURGBP, GBPJPY.
    -   **Avoid** exotics for simple strategies due to spread/volatility.

3.  **Backtesting (Initial Test)**
    -   Use `backtesting.py` or a custom vectorized loop.
    -   Timeframe: **1 Hour (1H)**.
    -   Period: Last 1-2 years (ensure enough samples).

## Template: Simple Strategy (Python)

```python
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()

# Run
bt = Backtest(GOOG, SmaCross, cash=10000, commission=.0002)
stats = bt.run()
bt.plot()
```

## Checklist before Optimization
- [ ] Does it work on at least 2 different pairs?
- [ ] Is the logic explainable (not "black box")?
- [ ] Are there at least 50 trades in the backtest period?
