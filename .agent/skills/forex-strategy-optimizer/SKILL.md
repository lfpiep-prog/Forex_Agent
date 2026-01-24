---
name: forex-strategy-optimizer
description: Advanced optimization techniques, parameter tuning, and walk-forward analysis to turn strategies profitable.
---

# Forex Strategy Optimizer

**Goal**: turn a "promising" strategy into a "profitable" and "robust" one.

## Workflow

1.  **Define Parameter Space**
    -   Identify tunable parameters (e.g., `SMA_Period`, `RSI_Threshold`, `StopLoss_Pips`).
    -   Set reasonable ranges (e.g., SMA: 10-200, step 10).

2.  **Grid Search Optimization**
    -   Run backtests for all combinations.
    -   **Metric**: Maximize `Sharpe Ratio` or `Profit Factor` (not just Net Profit).
    -   **Constraint**: Minimum `Trades > 50` (avoid overfitting to noise).

3.  **Robustness Check (Walk-Forward)**
    -   **In-Sample (Train)**: Optimize on data from Year X.
    -   **Out-of-Sample (Test)**: Run *best* parameters on Year X+1.
    -   If performance drops > 50%, the strategy is overfitted. Discard.

4.  **Portfolio Optimization**
    -   Combine uncorrelated strategies (e.g., EURUSD Trend + GBPJPY Mean Reversion).
    -   Adjust position sizing (risk management).

## Optimization Template (`backtesting.py`)

```python
stats = bt.optimize(
    n1=range(5, 30, 5),
    n2=range(10, 70, 5),
    maximize='Sharpe Ratio',
    constraint=lambda param: param.n1 < param.n2
)
print(stats['_strategy'])
```

## ⚠️ Warning
-   **Overfitting**: If you try 1000 parameters and find 1 good one, it's luck.
-   **Look-ahead Bias**: Ensure you don't use future data in the strategy logic.
