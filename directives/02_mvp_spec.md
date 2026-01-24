# 02 MVP Specification

## MVP Goal
Ein lokaler, modularer Trading-Loop, der historische Daten oder Mock-Daten verarbeitet, Signale generiert und Trades in einer Simulation ausführt (Paper Trading), um die Core-Logik ohne Broker-Abhängigkeit zu validieren.

## Inputs & Outputs
- **Inputs**: 
  - Historische Marktdaten (CSV oder `yfinance` Download).
  - Konfigurationsparameter (Risk settings, Strategy parameters).
- **Outputs**:
  - **Signale**: Buy/Sell/Hold Entscheidung pro Zeiteinheit.
  - **Trades**: Ausgeführte Orders mit Entry, Exit, PnL (in Simulations-Log/DB).
  - **Logs**: System-Logs (Error, Info) und Trading-Journal.

## Out of Scope
- Live Broker Integration (IBKR, OANDA, etc.) – *erst in Phase 2*.
- Real-time Data Streaming – *erst nach MVP*.
- Multi-Strategy Optimization / Genetic Algorithms.
- GUI / Web Interface (reines CLI/Log-file MVP).
- Portfolio Management über mehrere Konten.

## Akzeptanzkriterien
1. **Pipeline Run**: Ein Skript `python main.py` läuft ohne Fehler durch.
2. **Data Ingestion**: System liest Daten (z.B. EUR/USD H1 Candles) ein.
3. **Signal Generation**: Strategie erzeugt mindestens ein valides Signal basierend auf Mock-Daten.
4. **Execution Sim**: Ein Trade wird "geöffnet" und "geschlossen", PnL wird berechnet.
5. **Logging**: Eine Log-Datei bestätigt den Ablauf (`Order filled`, `PnL: +50`).

## Offene Entscheidungspunkte
1. **Data Provider**: Woher kommen die Testdaten? (Default: `yfinance` oder statische CSVs).
2. **Orchestrierung**: Wie läuft der Loop? (Default: Einfacher Python `while`-Loop oder Cron-Simulation).
3. **Persistenz**: Wo speichern wir Trades? (Default: JSON-File oder SQLite).
