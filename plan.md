Das ist der finale technische Beweis: Die **GRID Documentation** bestätigt, dass du Zugriff auf die "absolute Wahrheit" des Spiels hast, aber eben keine Informationen über die subjektive Sicht der Spieler (Vision).

Hier sind deine **konkreten nächsten Schritte**, die **To-dos** für den Start und der **Code-Baustein**, den du am Samstagmorgen als Erstes mit **Junie** (dem JetBrains AI Agent) zum Laufen bringen musst.

---

## 1. Sofortige To-dos (Vor dem Start)

* [ ] **API Access beantragen:** Geh sofort ins [GRID Portal](https://portal.grid.gg/) und registriere dich für den **"Open Access"**. Das kann bis zu 24–48h dauern. Ohne Key kein Projekt.
* [ ] **Sample Data sichern:** Suche in der Doku nach dem "Download Sample JSONL" Button. Du brauchst eine lokale Datei zum Testen, falls die API am Anfang hakt.
* [ ] **Tech-Stack bereitstellen:** Stelle sicher, dass `Node.js` (für React) oder `Python` (für das Backend) installiert sind und dein JetBrains-Editor (PyCharm/WebStorm) mit **Junie** verbunden ist.

---

## 2. Der "Winning" Code-Baustein (Backend-Logik)

Da wir die "Isolation" wegen fehlender Vision-Daten verworfen haben, ist dies dein Kern-Algorithmus für den **Formation Integrity Score**. Er ist robust, da er nur die Positionen deines eigenen Teams nutzt.

```python
import math

def calculate_cohesion_score(player_positions):
    """
    Berechnet die Formation Integrity basierend auf GRID x/y Koordinaten.
    player_positions: Liste von dicts [{'x': 120, 'y': 450}, ...]
    """
    if not player_positions or len(player_positions) < 2:
        return 100

    # 1. Schwerpunkt (Centroid) berechnen
    avg_x = sum(p['x'] for p in player_positions) / len(player_positions)
    avg_y = sum(p['y'] for p in player_positions) / len(player_positions)

    # 2. Durchschnittliche Distanz zum Schwerpunkt (Spread)
    total_dist = 0
    for p in player_positions:
        dist = math.sqrt((p['x'] - avg_x)**2 + (p['y'] - avg_y)**2)
        total_dist += dist
    
    avg_spread = total_dist / len(player_positions)

    # 3. Normalisierung (LoL Map ist ca. 15.000 Einheiten groß)
    # Ein Spread von < 800 ist sehr kompakt (Grouped), > 3000 ist Split.
    score = max(0, 100 - (avg_spread / 2500 * 100))
    return round(score, 2)

# Beispiel für die Integration:
# current_score = calculate_cohesion_score(grid_frame['blue_team_positions'])

```

---

## 3. Dein Schlachtplan für das Wochenende

### Samstag: Daten & Logik (Das Fundament)

1. **Parser bauen:** Lass Junie das GRID-JSONL-Format parsen. Nutze den Prompt: *"Junie, write a robust Python parser for GRID JSONL that extracts player coordinates and timestamps, handling missing data gracefully."*
2. **API Auth:** Implementiere den Header `x-api-key` gemäß der Doku, die du gefunden hast.
3. **Basic Chart:** Erstelle ein Frontend (React + Recharts), das den `Cohesion Score` über die Zeitachse anzeigt.

### Sonntag: Visualisierung & Pitch (Der "Wow"-Effekt)

1. **Causal Chain:** Verknüpfe Score-Abfälle mit Events (Kills/Towers).
2. **Heatmap:** Nutze `Plotly.js`, um die Positionen auf einer 2D-Map anzuzeigen.
3. **Pitch Recording:** Nutze das englische 90-Sekunden-Skript von oben. **Tipp:** Zeige im Video kurz den Chat mit Junie, wie sie den Parser schreibt – das lieben die Sponsoren.

---

## 4. Kritische Warnung für die Demo

GRID-Daten sind oft sehr "noisy" (viele Datenpunkte pro Sekunde).
**Tipp:** Berechne den Score nicht für jeden Frame, sondern nimm den Durchschnitt über 1 Sekunde (Sampling), sonst flackert dein Chart im Dashboard zu stark und sieht unruhig aus.

**Soll ich dir als nächstes den Prompt für Junie formulieren, mit dem du das JSON-Parsing und die Fehlerbehandlung perfekt automatisierst?**

Hervorragend, Thomas. Dass wir jetzt bei der interaktiven Map angekommen sind, ist der finale Meilenstein. Aber du hast recht: Wir dürfen vor lauter "Bling-Bling" den **technischen Kern** nicht aus den Augen verlieren, den wir in unserer Strategie (basierend auf dem Claude-Konzept) festgelegt hatten.

Hier ist die detaillierte technische Aufarbeitung dessen, was wir laut Plan umsetzen wollten, was wir erreicht haben und wie die Architektur die Anforderungen des Hackathons erfüllt:

---

### 1. Die Architektur: "Static Processing Pipeline"

Wir haben uns bewusst gegen ein Live-Backend entschieden, um die **Latenz- und Stabilitätsrisiken** zu eliminieren.

* **Soll-Zustand:** Ein System, das GRID-Daten in verwertbare Risk-Events transformiert.
* **Ist-Zustand:** Eine **Batch-Processing-Pipeline**.
* **Ingestion:** Python-Skript nutzt `httpx`, um den State-Point aus der REST/GQL-API zu ziehen.
* **Logic:** `core/analytics.py` fungiert als Transformer.
* **Storage:** Das "Nötigste" – eine flache `risk_timeline.json` als Datenbrücke (Decoupling von Engine und UI).



### 2. Der Kern-Algorithmus: "Oracle Heuristic"

Anstatt einer Blackbox (ML) haben wir uns auf eine **geometrische Heuristik** geeinigt, die wir im Pitch vollumfänglich erklären können.

* **Technisches Feature:** **Spatial Proximity Analysis**.
* **Berechnung:** Implementierung der euklidischen Distanzmatrix  für alle Spieler .
*  (Isolation Threshold)
*  (Threat Threshold)


* **Validation:** Der "Ground Truth" Abgleich. Wir haben die Heuristik gegen `deathEvents` validiert, um den **P-Value** (die statistische Signifikanz) unserer Vorhersage zu stützen.

### 3. Visualisierung: "State-Snapshot Dashboard"

Das Dashboard in `data/processed/risk_dashboard.html` ist kein reines Bild, sondern ein **Data-Viewer**.

* **Engine:** Plotly.js (eingebettet in HTML).
* **Layer 1 (Scatter):** Mapping der GRID-Koordinaten () auf ein standardisiertes 15.000 x 15.000 Grid (Summoner's Rift Map).
* **Layer 2 (Indikatoren):** Ein Gauge-Chart für den `Aggregation-Risk-Score`. Dieser berechnet sich aus der Summe der Isolations-Indizes, gewichtet nach der Rolle (`Carry` Gewichtung = 1.5x).
* **Value-Prop:** Wir zeigen nicht nur "wo" jemand ist, sondern den **Zustand des Systems** (Formation Integrity).

### 4. Was wir (geplant) weggelassen haben (Lean Strategy)

Um den 48-Stunden-Slot nicht zu sprengen, haben wir folgende Punkte gemäß Claude-Vorgabe gestrichen:

* **Kein Pathfinding:** Wir berechnen keine Wege, nur Distanz-Vektoren.
* **Kein Fog-of-War Simulation:** Wir nutzen "Omniscient Data" für die Post-Match Analyse.
* **Kein Echtzeit-Streaming:** Die Analyse läuft frame-basiert auf historischen oder gepufferten Daten.

---

### 📋 Zusammenfassung für dein Pitch-Deck (Technischer Part)

| Komponente | Technologie | Zweck |
| --- | --- | --- |
| **Data Fetcher** | Python / httpx | GRID API Kommunikation |
| **Risk Engine** | Python / Math-Module | Heuristische Distanz-Vektoranalyse |
| **Data Bridge** | JSON (statisch) | Entkopplung von Analyse und UI |
| **Dashboard** | Plotly / HTML | Interaktives Beweismittel für die Jury |

---

### Der letzte Schliff

Wir haben jetzt alles. Die Pipeline ist valide, die Zahlen sind durch den Korrelations-Check gedeckt und das Dashboard sieht nach "Pro-Tool" aus.

**Soll ich dir nun das versprochene "Pitch-Cheat-Sheet" schreiben?** Darin fasse ich die technischen USPs (Unique Selling Points) so zusammen, dass du auf Fragen wie *"Warum nicht einfach ein neuronales Netz?"* oder *"Wie präzise ist das bei Pro-Playern?"* die perfekte, datengestützte Antwort hast.