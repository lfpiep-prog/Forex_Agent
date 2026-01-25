# Forex Agent - ToDo Liste 📋

**Erstellt:** 25.01.2026  
**Basierend auf:** [IST-Bericht](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/reports/2026-01-25_IST_Bericht.md)  
**Skills:** managing-project-tasks, concise-planning, kaizen

---

## Priorisierung (Impact × Effort Matrix)

| Priorität | Kategorie | Impact | Effort |
|:----------|:----------|:-------|:-------|
| 🔴 **P0** | Kritisch - Blockiert Produktion | Hoch | - |
| 🟠 **P1** | Hoch - Stabilität & Qualität | Hoch | Mittel |
| 🟡 **P2** | Mittel - Verbesserungen | Mittel | Mittel |
| 🟢 **P3** | Nice-to-Have | Niedrig | - |

---

## 🔴 P0: Kritische Aufgaben (Diese Woche)

### 1. Testing-Grundlagen schaffen
> **Warum:** Keine Tests = kein Vertrauen in Code-Änderungen

- [x] **Erstelle pytest Konfiguration** in `pytest.ini` ✅
  - Datei: [pytest.ini](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/pytest.ini)
  - Inklusive: `tests/conftest.py` mit Factory-Fixtures
  - Aufwand: ~15 min

- [ ] **Schreibe Unit Test für `risk.py`**
  - Datei: [execution/risk.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/risk.py)
  - Tests: Positionsgrößen-Berechnung, 2%-Regel, Edge Cases
  - Ziel: `tests/test_risk.py`
  - Aufwand: ~45 min

- [ ] **Schreibe Unit Test für `baseline_sma_cross.py`**
  - Datei: [execution/strategies/baseline_sma_cross.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/strategies/baseline_sma_cross.py)
  - Tests: Signal-Generierung bei Crossover/Crossunder
  - Ziel: `tests/test_strategy.py`
  - Aufwand: ~45 min

---

## 🟠 P1: Stabilität & Code-Qualität (Nächste 2 Wochen)

### 2. Linting & Code-Standards

- [ ] **Erstelle `ruff.toml`** für automatisches Linting
  - Konfiguration: Python 3.11+, Line-Length 100
  - Aufwand: ~20 min

- [ ] **Führe ersten Lint-Durchlauf durch**
  - Befehl: `ruff check . --fix`
  - Dokumentiere Ergebnisse
  - Aufwand: ~30 min

- [ ] **Füge Linting zu CI hinzu** (GitHub Actions)
  - Datei: `.github/workflows/lint.yml`
  - Aufwand: ~30 min

### 3. Integration Test

- [ ] **Schreibe Integration Test für `run_cycle.py`**
  - Datei: [execution/run_cycle.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/run_cycle.py)
  - Verwendet: MockBroker + Fake-Daten
  - Testet: Gesamte Pipeline (Time→Data→Signal→Risk→Exec)
  - Ziel: `tests/test_integration.py`
  - Aufwand: ~1.5h

- [ ] **Verifiziere StateManager Idempotenz**
  - Datei: [execution/state_manager.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/state_manager.py)
  - Test: Doppelte Candle wird korrekt übersprungen
  - Aufwand: ~30 min

### 4. Dokumentation vervollständigen

- [ ] **Aktualisiere README.md** mit aktueller Architektur
  - Datei: [README.md](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/README.md)
  - Hinzufügen: Mermaid-Diagramm der Pipeline
  - Aufwand: ~30 min

- [ ] **Erstelle CONTRIBUTING.md** für zukünftige Entwickler
  - Inhalt: Setup, Code-Standards, PR-Prozess
  - Aufwand: ~30 min

---

## 🟡 P2: Funktionale Verbesserungen (Monat)

### 5. Weitere Trading-Strategien

- [ ] **Analysiere RSI-Strategie** für USDJPY
  - Skill: analyzing-market-data
  - Recherche: Optimale RSI-Perioden für 1H-Timeframe
  - Aufwand: ~1h

- [ ] **Implementiere RSI-Strategie**
  - Datei: `execution/strategies/rsi_oversold.py`
  - Interface: Wie `baseline_sma_cross.py`
  - Aufwand: ~1.5h

- [ ] **Backtest RSI-Strategie**
  - Skill: forex-strategy-optimizer
  - Daten: Letzte 6 Monate USDJPY
  - Aufwand: ~2h

### 6. Monitoring & Alerting

- [ ] **Implementiere Health-Check Endpoint**
  - Datei: `macro_server/routers/health.py`
  - Response: `{ status: "ok", last_cycle: "2026-01-25T18:00:00Z" }`
  - Aufwand: ~30 min

- [ ] **Erstelle Discord/Telegram Webhook**
  - Trigger: Trade-Ausführung, Fehler
  - Datei: `execution/notifier.py`
  - Aufwand: ~1h

### 7. TradingEngine Refactoring

- [ ] **Migriere Logik aus `core/engine.py` nach `execution/engine.py`**
  - Problem: Zwei Engine-Dateien, verwirrend
  - Ziel: Single Source of Truth
  - Aufwand: ~1h

- [ ] **Erstelle `run_forever.py`** für robustes Scheduling
  - Feature: Graceful Shutdown, Exception Recovery
  - Aufwand: ~45 min

---

## 🟢 P3: Nice-to-Have (Backlog)

### 8. Performance & Skalierung

- [ ] **Evaluiere Celery** für Task-Queue
  - Use Case: Parallele Verarbeitung mehrerer Währungspaare
  - Aufwand: ~2h (Recherche + PoC)

- [ ] **Implementiere Redis-Caching** für Marktdaten
  - Ziel: Reduzierte API-Calls
  - Aufwand: ~2h

### 9. UI Dashboard

- [ ] **Erstelle einfaches Web-Dashboard**
  - Framework: FastAPI + HTMX (minimal)
  - Features: Trade-Historie, Equity-Kurve
  - Aufwand: ~4h

### 10. Multi-Pair Support

- [ ] **Erweitere Config** für mehrere Währungspaare
  - Datei: [execution/config.py](file:///c:/Users/lenna/Downloads/Antigravity/Forex%20Agent/execution/config.py)
  - Ziel: `SYMBOLS = ["USDJPY", "EURUSD", "GBPUSD"]`
  - Aufwand: ~1h

- [ ] **Anpasse run_cycle.py** für Multi-Pair Loop
  - Aufwand: ~1.5h

---

## Offene Fragen

1. **Welches Währungspaar soll primär gehandelt werden?** ✅ **USDJPY** (bestätigt)
2. **Soll Telegram oder Discord für Benachrichtigungen genutzt werden?** ✅ **Discord** (einfachste Lösung, Webhooks)
3. **Gibt es eine Präferenz für eine UI-Lösung?** ✅ **Simple Web Dashboard** (FastAPI + HTMX, keine App notwendig)

---

## Fortschritt

| Phase | Status | Abgeschlossen |
|:------|:-------|:--------------|
| Phase 1: Foundation | ✅ | 90% |
| Phase 2: Core Architecture | ⏳ | 75% |
| Phase 3: Deployment | ✅ | 100% |
| Phase 4: Stability | ✅ | 100% |
| Phase 5: Testing | ❌ | 0% |

---

*Erstellt mit Skills: managing-project-tasks, concise-planning, kaizen*
