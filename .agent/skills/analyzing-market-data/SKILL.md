---
name: analyzing-market-data
description: Analyzes financial market data for trends and signals. Use when the user provides OHLCV data, asks for technical analysis, or mentions trading strategies.
---

# Market Data Analysis

## When to use this skill
- User provides a CSV of stock/forex data.
- User asks for indicators (SMA, RSI, MACD).
- User wants to backtest a trading strategy.

## Workflow
- [ ] **Ingest Data**: Load data from CSV or API (Pandas DataFrame).
- [ ] **Validate**: Check for `NaN` values, gaps in timestamps, and correct data types.
- [ ] **Calculate Indicators**: Apply mathematical functions (e.g., rolling averages).
- [ ] **Analyze Patterns**: Identify crossovers, divergences, or specific candlestick patterns.
- [ ] **Report/Visualize**: Output a summary table or generate a plot.

## Instructions
1.  **Data Integrity**:
    -   Ensure timestamps are parsed as `datetime` objects.
    -   Sort data by date (ascending).
2.  **Calculations**:
    -   Use `pandas` for vectorization (efficient) instead of loops (slow).
    -   Example SMA: `df['close'].rolling(window=14).mean()`
3.  **Risk Management**:
    -   When simulating trades, always track Drawdown and Sharpe Ratio.
    -   Do not look-ahead (ensure logic uses only *past* data).

## Resources
- `pandas`: Main data manipulation library.
- `matplotlib`/`plotly`: For visualization (if requested).
