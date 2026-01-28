---
name: strategy-testing-expert
description: Expertly operates the Strategy Test Center ("Spielwiese") to develop, backtest, and optimize Forex strategies using Polygon data. Use when the user asks to "test a strategy", "create a new strategy", "backtest", or mentions the "Spielwiese".
---

# Strategy Testing Expert

## When to use this skill
- User wants to create a new trading strategy (e.g., "Build an RSI strategy").
- User wants to backtest a hypothesis on historical data.
- User mentions "Spielwiese" or "Strategy Test Center".
- User wants to optimize parameters for an existing strategy.

## Workflow
1.  **Select/Create Strategy**: Check `execution/strategy_playground/strategies/` for existing strategies or create a new one inheriting from `backtesting.Strategy`.
2.  **Verify Data Interaction**: Ensure `execution/strategy_playground/loader.py` is used to fetch data.
3.  **Run Backtest**: Use `execution/strategy_playground/run_cli.py` for quick verification or `playground.ipynb` for detailed analysis.
4.  **Analyze Results**: Look at Sharpe Ratio, Return, and Drawdown.
5.  **Iterate**: Adjust parameters or logic based on results.

## Instructions

### 1. Creating a New Strategy
Create a new file in `execution/strategy_playground/strategies/<name>.py`.
**Template:**
```python
from backtesting import Strategy
from backtesting.lib import crossover
import talib # optional, or use pandas

class MyStrategy(Strategy):
    n1 = 10 # Define parameters as class variables for optimization

    def init(self):
        # Calculate indicators
        # self.I wrapper is critical for plotting!
        self.sma = self.I(lambda x: pd.Series(x).rolling(self.n1).mean(), self.data.Close)

    def next(self):
        # Logic per candle
        if self.data.Close[-1] > self.sma[-1]:
            self.buy()
        elif self.data.Close[-1] < self.sma[-1]:
            self.position.close()
```

### 2. Running a Backtest (CLI)
The `run_cli.py` script is the main entry point for automated testing.
**Command:**
```powershell
python execution/strategy_playground/run_cli.py
```
*Note: To change the strategy or symbol being tested by `run_cli.py`, you currently need to edit the `run_strategy()` call in `execution/strategy_playground/run_cli.py` or extend it to accept arguments.*

### 3. Data Loading
**ALWAYS** use the provided loader. It handles Polygon API authentication and formatting.
```python
from execution.strategy_playground.loader import load_data
df = load_data("EURUSD", "2024-01-01", "2024-06-01", timeframe='hour')
```

### 4. Interpretation Guidelines
- **Sharpe Ratio**: > 1 is good, > 2 is excellent. < 0 means risk-free rate is better.
- **Max Drawdown**: Should be minimized. High returns with -50% drawdown is usually unacceptable.
- **# Trades**: Ensure statistical significance (> 30 trades minimum).

## Resources
- `execution/strategy_playground/loader.py`: Data fetcher.
- `execution/strategy_playground/run_cli.py`: Test runner.
- `execution/strategy_playground/playground.ipynb`: Interactive lab.
