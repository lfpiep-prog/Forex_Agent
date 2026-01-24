# 03 Critical Decisions

| Entscheidung | Optionen | Benötigte Info | Default-Assumption |
| :--- | :--- | :--- | :--- |
| **Market Data Provider** | A) yfinance (free)<br>B) AlphaVantage<br>C) Statische CSVs | Budget? Echtzeit-Bedarf? | **A) yfinance** (für MVP ausreichend) |
| **Broker / Execution** | A) IG Markets (Primary)<br>B) IBKR (Future) | API Keys vorhanden? | **IG Markets** (REST API) |
| **Orchestrierung** | A) Main-Loop script<br>B) Systemd/Cron<br>C) n8n / Airflow | Server-Umgebung vorhanden? | **A) Main-Loop script** (lokal startbar) |
| **Persistenz Layer** | A) JSON Files<br>B) SQLite<br>C) PostgreSQL | Datenvolumen? | **B) SQLite** (einfach, relational) |
| **Backtesting Engine** | A) Custom Loop<br>B) Backtrader<br>C) Lean (QuantConnect) | Komplexität der Strategie? | **A) Custom Loop** (für maximale Kontrolle im MVP) |
