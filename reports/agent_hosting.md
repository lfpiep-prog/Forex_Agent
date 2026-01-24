# Hosting & Operations Report: Forex Agent

## 1. Skills Inventory
Inventur der gescannten Skills unter `@[.agent/skills]`:

| Skill | Zweck (aus SKILL.md) |
| :--- | :--- |
| **analyzing-market-data** | Analyzes financial market data for trends and signals. |
| **api-patterns** | API design principles and decision-making. |
| **architecture** | Architectural decision-making framework. |
| **backend-dev-guidelines** | Comprehensive backend development guide. |
| **cc-skill-security-review** | Security review checklist and patterns. |
| **clean-code** | Pragmatic coding standards - concise, direct. |
| **code-review-checklist** | Checklist for conducting thorough code reviews. |
| **concise-planning** | Generates clear, actionable, and atomic checklists. |
| **creating-skills** | Generates .agent/skills/ directories. |
| **debugging-code-systematically** | Debugs code using a hypothesis-driven approach. |
| **designing-modern-ui** | Designs modern, responsive UIs. |
| **documentation-templates** | Documentation templates and structure guidelines. |
| **file-organizer** | Intelligently organizes files and folders. |
| **forex-strategy-creator** | Workflow for generating 1H candle strategies. |
| **forex-strategy-optimizer** | Advanced optimization techniques and tuning. |
| **git-pushing** | Stage, commit, and push git changes. |
| **kaizen** | Guide for continuous improvement and standardization. |
| **lint-and-validate** | Automatic quality control and linting. |
| **managing-project-tasks** | Organizes project tasks and manages TODOs. |
| **planning-with-files** | Implements Manus-style file-based planning. |
| **product-manager-toolkit** | Toolkit for product managers (RICE, PRD, etc.). |
| **prompt-engineering** | Strategies for effective prompting. |
| **python-patterns** | Python development principles and decision-making. |
| **react-best-practices** | Performance optimization guide for React/Next.js. |
| **senior-architect** | Software architecture skill for scalable systems. |
| **software-architecture** | Guide for quality focused software architecture. |
| **systematic-debugging** | Hypothesis-driven debugging approach. |
| **testing-patterns** | Jest testing patterns and TDD info. |
| **writing-plans** | Planning before coding. |
| **writing-professional-docs** | Drafts high-quality, professional documentation. |

---

## 2. Ist-Stand Analyse
- **Entry-Point**: `main_loop.py` ist der primäre Entry-Point für den Agenten.
- **Scheduler**: Die Datei implementiert bereits eine `while True` Schleife, die stündlich (`sleep`) pausiert. Ein externer Scheduler (Cron) ist daher nicht zwingend notwendig, aber ein Supervisor (Docker/Systemd) ist für den Restart wichtig.
- **Config**: Umgebungsvariablen werden via `.env` geladen.
- **Architektur**: Python-Skript. Nebenläufig existiert `macro_server` (FastAPI) mit eigenem `Dockerfile` und Deployment auf Railway.
- **Host-Umgebung**: Aktuell lokal (Windows). Code ist aber plattformunabhängig (Python).

## 3. Zielbild & Maßnahmen
Um "headless run", "restart bei crash" und "logs verfügbar" zu erreichen, ist eine **Containerisierung (Docker)** der sauberste Weg, da dies bereits im Projekt (`macro_server`) verwendet wird und die Abhängigkeiten kapselt.

**Lösung:**
- **Neues Dockerfile** im Root für den Agenten.
- **Restart Policy**: Docker übernimmt den Restart (`--restart unless-stopped`).
- **Logs**: Docker Logs (`docker logs`) kapseln stdout/stderr.
- **Headless**: Docker Container läuft im Hintergrund (`-d`).

## 4. Anleitung (Runbook)

### Vorbereitung
1.  Sicherstellen, dass Docker Desktop (Windows) oder Docker Engine (Linux) läuft.
2.  `.env` Datei prüfen (WICHTIG: `IG_ACC_TYPE=DEMO` für Sicherheit).

### Starten (Docker)
Führen Sie folgende Befehle im Terminal (PowerShell oder Bash) im Projekt-Root aus:

```bash
# 1. Image bauen
docker build -t forex-agent .

# 2. Container starten (Hintergrund, Auto-Restart beim Boot/Crash)
docker run -d --name forex-agent --restart unless-stopped --env-file .env forex-agent
```

### Wartung
- **Logs prüfen**: `docker logs -f forex-agent`
- **Stoppen**: `docker stop forex-agent`
- **Update**: Nach Code-Änderungen erneut `docker build ...` und `docker run ...` ausführen.

### Alternative: Windows Native (falls kein Docker gewünscht)
Falls Docker keine Option ist, kann das Skript einfach in einer PowerShell-Loop gestartet werden (einfach, aber weniger robust als Docker):

```powershell
python main_loop.py
```
*Hinweis: Dies bietet keinen automatischen Restart nach einem Crash oder Reboot.*

### Guardrails
- Im `Dockerfile` wird ein Non-Root User verwendet.
- `IG_ACC_TYPE` muss in `.env` auf `DEMO` stehen, sonst führt der Agent echte Trades aus.
