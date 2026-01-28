# Strategy Test Center (Die "Spielwiese")

Hier kannst du Forex-Strategien mit echten historischen Daten von Polygon entwickeln und testen.

## 🚀 Schnellstart

### Option 1: Interaktiv (Empfohlen)
Öffne die Datei `playground.ipynb` in VS Code oder Jupyter.
Dies ist dein interaktives Labor. Du kannst:
1.  Code-Zellen einzeln ausführen (`Shift + Enter`).
2.  Daten live laden und inspizieren.
3.  Strategie-Parameter ändern und sofort das Ergebnis sehen.
4.  Plots interaktiv zoomen.

### Option 2: Terminal
Führe das Test-Skript direkt aus:
```bash
python execution/strategy_playground/run_cli.py
```
Dies ist nützlich für schnelle Checks, ob alles läuft.

## 🛠 Neue Strategie erstellen

1.  Gehe in den Ordner `strategies/`.
2.  Erstelle eine neue Python-Datei (z.B. `rsi_strategy.py`).
3.  Erbe von der Klasse `Strategy` (aus `backtesting`).
4.  Implementiere `init()` (Indikatoren berechnen) und `next()` (Logik für Kauf/Verkauf).

Beispiel:
```python
from backtesting import Strategy
from backtesting.lib import crossover

class MeineStrategie(Strategy):
    def init(self):
        # Indikatoren hier berechnen (z.B. self.I(...))
        pass

    def next(self):
        # Kauf/Verkauf Logik
        if self.data.Close[-1] > ...:
            self.buy()
```

5.  Importiere und nutze deine neue Strategie im `playground.ipynb` oder `run_cli.py`.

## 📊 Daten
Der `Data Loader` (`loader.py`) holt automatisch Daten von der Polygon API.
Achte darauf, dass deine `.env` Datei einen gültigen `POLYGON_API_KEY` enthält.
