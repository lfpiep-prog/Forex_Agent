# 06 Data Contract

## Overview
This document defines the standard schema for market data internal to the Forex Agent. All ingestion scripts must normalize data to this format.

## Schema
Format: **CSV** (Active MVP format) or **Parquet** (Preferred for production).

> [!NOTE]
> Switched to CSV for MVP due to environment issues with `pyarrow` installation.


| Field Name | Type | Description | Required | Validation Rule |
| :--- | :--- | :--- | :--- | :--- |
| `timestamp` | datetime64[ns, UTC] | ISO8601 UTC timestamp | Yes | Unique per symbol, Strictly increasing |
| `symbol` | string | Pair name (e.g., 'EURUSD') | Yes | format: ^[A-Z]{6}$ or similar |
| `open` | float64 | Open Price | Yes | > 0 |
| `high` | float64 | High Price | Yes | >= open, >= low, >= close |
| `low` | float64 | Low Price | Yes | > 0, <= high, <= open, <= close |
| `close` | float64 | Close Price | Yes | > 0 |
| `volume` | float64 | Tick or Trade Volume | No | >= 0 (default 0 if missing) |

## Granularity
- **M1** (1 Minute) is the primary base granularity.
- Higher timeframes (H1, D1) are derived from M1 where possible, or fetched explicitly if needed.

## Timezone
- **ALWAYS UTC**. No local times.

## Storage Structure
`data/processed/{symbol}/{granularity}.parquet`
e.g., `data/processed/EURUSD/M1.parquet`
