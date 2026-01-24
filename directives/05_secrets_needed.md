# 05. Secrets & Envs Needed

**Status:** Draft (Waiting for Decision)
**Zweck:** Definition der notwendigen `.env` Variablen.

Diesen Katalog kopieren wir später in `.env.example`. Aktuell noch leer lassen (Sicherheitsrisiko).

---

## 1. Broker Secrets (Je nach Wahl)

### Option A: Interactive Brokers (IBKR) [FUTURE / LATER]
- `IBKR_ACCOUNT_ID`: Die IBKR Account Nummer (z.B. U1234567)
- `IBKR_HOST`: Hostname der TWS/Gateway (default: 127.0.0.1)
- `IBKR_PORT`: Port der API (default: 7497 für Paper, 7496 für Live)

### Option B: IG Markets [ACTIVE / REQUIRED]
- `IG_USERNAME`: Login Username (Live oder Demo)
- `IG_PASSWORD`: Login Password
- `IG_API_KEY`: Generierter API Key aus dem 'My Account' settings panel
- `IG_ACC_TYPE`: `DEMO` (für den Anfang)
- `IG_ACCOUNT_ID`: Die spezifische Account-ID (optional, falls mehrere vorhanden)

---

## 2. Data Feed Secrets (Je nach Wahl)

### Option A: Twelve Data
- `TWELVEDATA_API_KEY`: API Key

### Option B: Tiingo
- `TIINGO_API_KEY`: API Key

---

## 3. General / System
- `FLASK_SECRET_KEY`: (Später für Web-GUI benötigt)
- `LOG_LEVEL`: `INFO` oder `DEBUG`
