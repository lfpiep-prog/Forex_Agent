# 10. Orchestration Options

**Status:** Draft
**Ziel:** Definition der Deployment- und Steuerungsstrategie für den Forex Bot.

---

## Option A: Python Native Service / Cron
Der Bot läuft als eigenständiger Prozess auf einem Server (VPS).

### Setup
1. **OS Level Cron (Linux):**
   - Eintrag in Crontab: `*/60 * * * * /path/to/venv/bin/python /path/to/execution/run_cycle.py`
   - Vorteil: Simpel, robust, keine externen Abhängigkeiten.
   - Nachteil: Schwieriger zu monitoren ohne extra Dashboard.

2. **Systemd Service:**
   - Einrichten eines `forex-bot.service` Files.
   - Kann als Endlos-Loop laufen (`while True: sleep(3600)`).
   - Vorteil: Auto-Restart bei Crash, Logs via `journalctl`.

### Pro/Con
- **Pro:** Volle Kontrolle, keine externen Kosten/Tools.
- **Con:** "Black Box", man muss sich aktiv einloggen um Status zu prüfen.

---

## Option B: N8N Bridge (Empfohlen für Low-Code Observability)
N8N dient als "Control Tower" und Trigger.

### Workflow
1. **N8N Schedule Trigger:**
   - Läuft z.B. jede Stunde.
2. **Execute Command Node:**
   - Führt lokal (auf dem gleichen Server) `python execution/run_cycle.py` aus.
   - Oder ruft einen einfachen Flask-Wrapper Endpoint auf.
3. **Result Processing:**
   - Liest den Output (JSON Log oder Return Code).
   - **Bei Erfolg:** Loggt in eine Google Sheet / Notion DB.
   - **Bei Fehler:** Sendet Telegram/Slack Alert an den Nutzer.

### Pro/Con
- **Pro:** Exzellente Observability "Out of the box". Fehler-Benachrichtigung einfach klickbar.
- **Con:** N8N muss gehostet werden (Self-hosted oder Cloud).

---

## Empfehlung für MVP
Start mit **Option B (N8N)**, falls N8N vorhanden ist. Dies ermöglicht sofortiges Mobile-Alerting via Telegram ohne Code-Aufwand.
Falls kein N8N vorhanden: **Option A (Cron)** mit Log-File Überwachung.
