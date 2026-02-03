import json
import math
import os
import sys

# Konstanten (wie in analytics.py)
LCI_ALLY_DIST = 800
LCI_ENEMY_DIST = 1400
CARRIES = ["mid", "adc"]

def get_distance(p1, p2):
    return math.sqrt((p2['x'] - p1['x'])**2 + (p2['y'] - p1['y'])**2)

def calculate_frame_risk(players):
    """Berechnet den Risk-Score für einen einzelnen Frame."""
    risk_score = 0
    # Wir brauchen Team-Zuordnung
    # In real_data.json sind sie nach Teams gruppiert
    # Wir flachen das kurz ab für die Distanzberechnung
    
    for p in players:
        if p.get('role') not in CARRIES: continue
        
        # Verbündete (selbes Team)
        allies = [a for a in players if a['team_idx'] == p['team_idx'] and a['id'] != p['id']]
        # Gegner
        enemies = [e for e in players if e['team_idx'] != p['team_idx']]
        
        min_ally_dist = min([get_distance(p, a) for a in allies], default=9999)
        min_enemy_dist = min([get_distance(p, e) for e in enemies], default=9999)
        
        if min_ally_dist > LCI_ALLY_DIST and min_enemy_dist < LCI_ENEMY_DIST:
            risk_score += 20
            
    return risk_score

def validate():
    filepath = "data/raw/real_data.json"
    if not os.path.exists(filepath):
        print(f"FEHLER: {filepath} nicht gefunden.")
        return

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Wir extrahieren die Spieler aus dem vorhandenen Snapshot
        games = raw_data.get("data", {}).get("seriesState", {}).get("games", [])
        if not games:
            print("Keine Spieldaten gefunden.")
            return

        # Da wir nur einen Snapshot haben, "simulieren" wir die Validierung
        # oder weisen darauf hin, dass für eine echte Korrelation mehr Daten nötig sind.
        
        # Spieler extrahieren und Rollen zuweisen
        all_players = []
        for t_idx, team in enumerate(games[0].get("teams", [])):
            for i, p in enumerate(team.get("players", [])):
                pos = p.get("position")
                if pos and pos.get("x") is not None:
                    p_data = {
                        "id": p.get("id"),
                        "name": p.get("name"),
                        "team_idx": t_idx,
                        "x": pos["x"],
                        "y": pos["y"],
                        "role": "mid" if i == 2 else ("adc" if i == 3 else "other"),
                        "is_alive": True # Heuristik
                    }
                    all_players.append(p_data)

        # Simulation eines Todes-Events (da im Snapshot evtl. keine Historie ist)
        # Wir prüfen den aktuellen Frame
        current_risk = calculate_frame_risk(all_players)
        
        print("=== VALIDIERUNGS-REPORT ===")
        print(f"Anzahl analysierter Tode: 0 (Snapshot-Modus)")
        print(f"Aktueller Risk-Score im Snapshot: {current_risk}")
        
        # Heuristische Bewertung
        if current_risk > 0:
            print("Korrelations-Faktor: N/A (Nur ein Frame verfügbar)")
            print("\nERGEBNIS: Die Heuristik erkennt Isolation im aktuellen Snapshot.")
            print("HINWEIS: Für eine statistische Korrelation (15s Fenster) wird ein JSONL-Stream benötigt.")
        else:
            print("\nERGEBNIS: Keine Isolation im aktuellen Snapshot erkannt.")
            
    except Exception as e:
        print(f"Fehler bei der Validierung: {e}")

if __name__ == "__main__":
    validate()

