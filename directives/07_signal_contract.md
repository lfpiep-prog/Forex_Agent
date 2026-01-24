# Signal Contract

This document defines the interface for signal generation.

## 1. Input: Normalized Prices

The signal engine expects input data in a standardized format, typically a Pandas DataFrame or a list of dictionaries/objects, containing at least the following fields:

- `timestamp` (datetime): The time of the candle close.
- `open` (float)
- `high` (float)
- `low` (float)
- `close` (float)
- `volume` (float, optional)
- `symbol` (string): The instrument pair (e.g., "EURUSD").

## 2. Output: Signal Events

Strategies must return a list of `SignalEvent` objects (or dictionaries) with the following structure:

- `timestamp` (datetime): Time the signal was generated (usually the close time of the triggering candle).
- `symbol` (string): The instrument.
- `direction` (string or int):
  - `LONG` (or 1)
  - `SHORT` (or -1)
  - `FLAT` (or 0) - *Optional, for closing positions explicitly*
- `confidence` (float, optional): 0.0 to 1.0 value indicating strength. Default 1.0.
- `rationale` (string): A human-readable text explaining WHY the signal was triggered (e.g., "SMA(50) crossed above SMA(200)").

## 3. Usage

The `generate_signals.py` script will be the main entry point to run strategies against data.
Strategies should be located in `execution/strategies/` and adhere to this contract.
