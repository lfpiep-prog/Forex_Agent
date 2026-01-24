# 04. Broker & Market Data Matrix

**Status:** Draft (Assessment Phase)
**Ziel:** Auswahl der besten Komponenten für einen DE/EU-basierten Forex Agenten (Constraint: KEIN OANDA).

---

## 1. Broker Options (Execution)
*Muss API-Trading für DE-Residents erlauben.*

| Kandidat | Warum geeignet? | Pros | Cons | Was muss der Nutzer liefern? |
| :--- | :--- | :--- | :--- | :--- |
| **Interactive Brokers (IBKR)** | Einer der grössten, sichersten Broker weltweit. Exzellente API (TWS/Gateway). Akzeptiert DE-Kunden problemlos. | - Profi-Level Execution<br>- Sehr günstige Commissions<br>- Starke Python-Libs (`ib_insync`) | - Hohe Einstiegshürde (Software TWS muss laufen)<br>- Komplexes Setup<br>- Market Data oft kostenpflichtig | - Funded Live Account<br>- TWS/Gateway installiert<br>- API-Port & Account ID |
| **IG Markets (IG Europe)** | Sehr populär in Europa/DE. Bietet REST & Streaming API. | - Einfachere API-Struktur als IBKR<br>- Gute "Risk Management" Features (Guaranteed Stop)<br>- DMA (Direct Market Access) möglich | - Spreads teils höher als bei ECN Brokern<br>- API-Doku manchmal lückenhaft | - Live Account (IG Europe)<br>- API Key<br>- Username/Password |
| **Dukascopy** | Schweizer Bank & Broker. Starker Fokus auf Algo-Trading (JForex). | - Sehr zuverlässig<br>- Historische Tick-Daten exzellent | - API ist nativ **Java** (Python via Bridge möglich, aber komplexer)<br>- Eher für fortgeschrittene Devs | - Live Account<br>- JForex API Zugangsdaten |

**Empfehlung:** Start mit **IBKR** (via `ib_insync` library) oder **IG Markets** je nach Präferenz für Komplexität vs. Komfort.

---

## 2. Market Data Options (Analysis)
*Unabhängige Datenfeeds für robustere Signale (Backup oder Primary).*

| Kandidat | Warum geeignet? | Features (Forex) | Kosten / Free Tier | Was muss der Nutzer liefern? |
| :--- | :--- | :--- | :--- | :--- |
| **Twelve Data** | Moderne, sehr einfache REST & WebSocket API. Python-Native SDK. | - Real-time Rates<br>- Technical Indicators endpoint | - **Free:** 800 credits/day (reicht für MVP)<br>- **Paid:** ab ~$29/mo für mehr Limits | - API Key (Email signup) |
| **Tiingo** | Bekannt für gute Qualität und "Firehose" Websocket support auch im Free Tier. | - Forex Websocket (Top-of-Book)<br>- Clean Historical Data | - **Free:** 500 unique symbols/month, 50 GB bandwidth (sehr grosszügig) | - API Key |
| **Alpha Vantage** | Klassiker für Financial Data APIs. | - Standard Forex Paare<br>- Daily/Intraday | - **Free:** 25 requests/day (Sehr limitiert inzwischen!) | - API Key |

**Empfehlung:** **Tiingo** oder **Twelve Data** für Marktdaten. Alpha Vantage ist mittlerweile zu strikt im Free Tier.

---

## 3. Decision Required
Bitte bestätige im nächsten Prompt die Präferenz:
1.  **Broker:** IBKR oder IG?
2.  **Data:** Tiingo oder Twelve Data?
