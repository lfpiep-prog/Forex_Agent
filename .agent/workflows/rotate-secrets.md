---
description: Secret rotation schedule and procedures for Forex Agent credentials
---

# Secret Rotation Workflow

Regelmäßige Rotation von Credentials erhöht die Sicherheit.

## Rotationsplan

| Secret | Frequenz | Letzte Rotation | Nächste |
|--------|----------|-----------------|---------|
| IG API Key | 90 Tage | TBD | TBD |
| Discord Webhook | Bei Verdacht | TBD | TBD |
| SSH Keys | Jährlich | TBD | TBD |

## Rotation durchführen

### 1. IG API Key

```bash
# 1. Neuen Key im IG Dashboard generieren
# 2. Auf Server .env aktualisieren:
ssh forex
nano ~/Forex_Agent/.env
# 3. Container neu starten:
docker compose down && docker compose up -d
```

### 2. Discord Webhook

```bash
# 1. Neuen Webhook im Discord Server erstellen
# 2. .env auf Server aktualisieren
# 3. Alten Webhook in Discord löschen
```

### 3. SSH Keys

```bash
# Lokal: Neuen Key generieren
ssh-keygen -t ed25519 -f ~/.ssh/forex_new

# Neuen Public Key auf Server hinzufügen
ssh forex "echo 'NEUER_PUBLIC_KEY' >> ~/.ssh/authorized_keys"

# Testen mit neuem Key
ssh -i ~/.ssh/forex_new forex

# Alten Key entfernen
ssh forex "sed -i '/ALTER_KEY_FINGERPRINT/d' ~/.ssh/authorized_keys"
```

## Nach Rotation

- [ ] Testen ob Services funktionieren
- [ ] Datum in Tabelle oben aktualisieren
- [ ] Alte Credentials sicher löschen
