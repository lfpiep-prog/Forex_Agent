# Agent Execution Flow Dokumentation

**Datum:** 24.01.2026  
**Status:** Analyse der aktuellen Codebasis  

Dieses Dokument fasst die Dateien und Module zusammen, die den automatisierten Ablauf des Forex Agents steuern – von der Informationsbeschaffung bis zur Orderausführung und Dokumentation.

## 1. Hauptsteuerung (Orchestration)
Der zentrale Einstiegspunkt, der den gesamten Zyklus koordiniert.
*   **[execution/run_cycle.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/run_cycle.py)**: Steuert den Ablauf Schritt für Schritt:
    1.  Zeit-Check (Trading Hours)
    2.  Datenabruf (Prices)
    3.  Strategie-Analyse (Signals)
    4.  News-Filter (Sentiment)
    5.  Risiko-Prüfung & Positionsgröße
    6.  Order-Ausführung

## 2. Informationsbeschaffung (Data Fetching)
Verantwortlich für das Sammeln von Marktdaten.
*   **[execution/market_data.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/market_data.py)**: Abstrahiert die Datenquellen. Nutzt Adapter für:
    *   `YFinanceAdapter`: Für Backtests/historische Daten.
    *   `BrokerAPIAdapter`: Für Live-Daten vom IG Broker.
    *   `TwelveDataAdapter`: Als alternative Quelle.
*   **[data/mcp_client.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/data/mcp_client.py)**: Holt externe Daten (z.B. News-Sentiment) für den Filter-Schritt.

## 3. Strategieanwendung (Strategy & Signals)
Hier wird entschieden, ob gehandelt wird.
*   **[execution/generate_signals.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/generate_signals.py)**: Lädt die gewählte Strategie dynamisch.
*   **[execution/strategies/baseline_sma_cross.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/strategies/baseline_sma_cross.py)**: Konkrete Implementierung der Handelslogik (z.B. SMA Cross).
*   **[execution/filters.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/filters.py)**: Zusätzliche Filter (z.B. `TimeFilter`), um Handel außerhalb der Marktzeiten zu verhindern.

## 4. Ordererstellung & Risiko (Execution with SL/TP)
Umwandlung des Signals in eine konkrete Order mit Risikomanagement.
*   **[execution/risk.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/risk.py)**:
    *   Berechnet die Positionsgröße (Lots) basierend auf dem Kontostand (2% Risiko-Regel).
    *   Validiert Stop Loss (SL) Distanzen.
    *   Berechnet Pip-Werte für korrekte Größenbestimmung.
*   **[execution/execute_order.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/execute_order.py)**:
    *   Erstellt das `OrderIntent` Objekt.
    *   Mappt SL/TP Preise in Distanzen (für Broker, die Distanzen erwarten).
    *   Verwaltet Idempotenz (verhindert doppelte Ausführung).
*   **[execution/brokers/ig_broker.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/brokers/ig_broker.py)**: Die Schnittstelle zur IG Handelsplattform für die finale Platzierung.

## 5. Dokumentierung (Logging)
Nachverfolgung aller Aktionen.
*   **[execution/logger.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/logger.py)**:
    *   Schreibt technische Logs (für Debugging) in JSONL-Dateien.
    *   Schreibt die geschäftliche Logik in das `trade_journal.csv` (CSV-Format).
*   **[execution/run_cycle.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/run_cycle.py)**: Ruft den Logger nach jedem Schritt auf, um Status ("PASSED", "BLOCKED", "ERROR") und Entscheidungen festzuhalten.
