import json
import math
import os
import sys

# Konstanten
ISOLATION_THRESHOLD = 3500
CARRIES = ["mid", "adc"]  # Rollen-Mapping (Heuristik)

# Schwellenwerte für den Lonely Carry Index
LCI_ALLY_DIST = 1000
LCI_ENEMY_DIST = 1400

# Normalisierungsfaktor für den Cohesion Score (Map-Größe Heuristik)
COHESION_SPREAD_MAX = 2500 

# Teamfight Detection Constants
TF_PLAYER_DISTANCE = 2000
TF_MIN_PLAYERS_PER_TEAM = 3

# Predefined Impact Weights (Based on Esports Analytics Research)
EVENT_IMPACTS = {
    "dragon_lost": -6,      # % Win Probability impact
    "baron_lost": -12,
    "tower_lost": -3,
    "death_carry": -4,      # ADC/Mid death
    "death_support": -2,
    "gold_swing_1k": -2,    # Per 1000 gold
    "isolation_risk": -5    # New: Risk from bad positioning
}

def build_causal_chain(risk_delta):
    """
    Explains risk drop using weighted events.
    In a real scenario, this would look at actual events in a time window.
    For the MVP/Demo, we attribute the risk delta to likely causes.
    """
    chain = []
    remaining_delta = risk_delta
    
    # Heuristik: Wenn das Risiko hoch ist, ist die Isolation oft der Hauptgrund
    if remaining_delta < -3:
        impact = EVENT_IMPACTS["isolation_risk"]
        chain.append({
            "cause": "Bad Positioning (Isolated Carry)",
            "impact": impact
        })
        remaining_delta -= impact
    
    # Weitere Faktoren (Dummy/Heuristik für Demo)
    if remaining_delta < -2:
        chain.append({
            "cause": "Vision Gap",
            "impact": -2
        })
        remaining_delta -= -2
        
    return chain

def detect_teamfight(all_players_by_team):
    """
    Erkennt einen Teamfight basierend auf der Proximity der Spieler.
    """
    if len(all_players_by_team) < 2:
        return False
        
    blue_team = all_players_by_team[0]
    red_team = all_players_by_team[1]
    
    # Zähle Spieler in der Nähe voneinander
    blue_near_red = 0
    for b in blue_team:
        for r in red_team:
            if get_distance(b, r) < TF_PLAYER_DISTANCE:
                blue_near_red += 1
                break # Dieser Blue-Spieler ist nah an mindestens einem Red-Spieler
                
    red_near_blue = 0
    for r in red_team:
        for b in blue_team:
            if get_distance(r, b) < TF_PLAYER_DISTANCE:
                red_near_blue += 1
                break
                
    return blue_near_red >= TF_MIN_PLAYERS_PER_TEAM and red_near_blue >= TF_MIN_PLAYERS_PER_TEAM

def get_distance(p1, p2):
    """Berechnet die euklidische Distanz zwischen zwei Punkten."""
    return math.sqrt((p2['x'] - p1['x'])**2 + (p2['y'] - p1['y'])**2)

def calculate_cohesion_score(player_positions):
    """
    Berechnet die Formation Integrity (Cohesion Score) basierend auf GRID x/y Koordinaten.
    player_positions: Liste von dicts [{'x': 120, 'y': 450}, ...]
    """
    if not player_positions or len(player_positions) < 2:
        return 100.0

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
    score = max(0, 100 - (avg_spread / COHESION_SPREAD_MAX * 100))
    return round(score, 2)

def load_data(filepath):
    """Lädt die GRID-Daten."""
    if not os.path.exists(filepath):
        print(f"FEHLER: Datei {filepath} nicht gefunden.")
        sys.exit(1)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"FEHLER beim Laden der JSON: {e}")
        sys.exit(1)

def map_roles(players):
    """
    Weist den Spielern Rollen zu (Heuristik).
    """
    for i, p in enumerate(players):
        if i == 2:
            p['role'] = 'mid'
        elif i == 3:
            p['role'] = 'adc'
        else:
            p['role'] = 'other'
    return players

def analyze_frame(game_data):
    """Analysiert einen einzelnen Game-Snapshot."""
    teams = game_data.get("teams", [])
    if len(teams) < 2:
        return None

    frame_results = {
        "teams": [],
        "risk_events": []
    }

    all_players_by_team = []
    for t_idx, team in enumerate(teams):
        team_players = []
        for p in team.get("players", []):
            # Filtering: Nur Spieler mit Koordinaten und (falls vorhanden) Status 'alive'
            pos = p.get("position")
            is_alive = p.get("alive", True) # Default zu True, falls Feld fehlt
            
            if pos and pos.get("x") is not None and is_alive:
                team_players.append({
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "x": pos["x"],
                    "y": pos["y"]
                })
        all_players_by_team.append(map_roles(team_players))

    for t_idx in range(2):
        own_team = all_players_by_team[t_idx]
        enemy_team = all_players_by_team[1 - t_idx]
        
        # Cohesion Score berechnen
        cohesion = calculate_cohesion_score(own_team)
        
        # Teamfight Detection
        is_teamfight = detect_teamfight(all_players_by_team)
        
        # Risiko-Analyse (Lonely Carry)
        isolation_alerts = []
        causal_chains = []
        for p in own_team:
            if p['role'] not in CARRIES:
                continue
            
            min_ally_dist = min([get_distance(p, a) for a in own_team if a['id'] != p['id']], default=9999)
            min_enemy_dist = min([get_distance(p, e) for e in enemy_team], default=9999)
            
            if min_ally_dist > LCI_ALLY_DIST and min_enemy_dist < LCI_ENEMY_DIST:
                alert = {
                    "player": p['name'],
                    "role": p['role'],
                    "dist_ally": round(min_ally_dist, 1),
                    "dist_enemy": round(min_enemy_dist, 1)
                }
                isolation_alerts.append(alert)
                
                # Causal Chain für diese Isolation generieren
                # Wir nehmen an, dass eine Isolation ca. -5% WP Impact hat
                causal_chains.append(build_causal_chain(-5))

        frame_results["teams"].append({
            "team_idx": t_idx,
            "cohesion_score": cohesion,
            "is_teamfight": is_teamfight,
            "isolation_alerts": isolation_alerts,
            "causal_chains": causal_chains
        })

    return frame_results

def run_analysis():
    DATA_PATH = "data/raw/real_data.json"
    OUTPUT_PATH = "data/processed/analytics_report.json"
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    raw_data = load_data(DATA_PATH)
    series_state = raw_data.get("data", {}).get("seriesState", {})
    games = series_state.get("games", [])
    
    if not games:
        print("Keine Spieldaten gefunden.")
        return

    # Wir analysieren den aktuellsten Snapshot
    latest_game = games[0]
    results = analyze_frame(latest_game)
    
    if results:
        # Metadaten hinzufügen
        results["series_id"] = series_state.get("id")
        
        with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n[OK] Analyse abgeschlossen. Ergebnisse in {OUTPUT_PATH}")
        print(f"--- Series ID: {results['series_id']} ---")
        for t in results["teams"]:
            team_name = "Blue" if t['team_idx'] == 0 else "Red"
            print(f"\nTeam {team_name}:")
            print(f"  Formation Integrity (Cohesion): {t['cohesion_score']}%")
            if t['is_teamfight']:
                print("  [EVENT] Teamfight erkannt!")
            if t['isolation_alerts']:
                for alert in t['isolation_alerts']:
                    # Winning Story: Totenkopf-Icon für erfolgreiche Vorhersagen
                    # (In einem echten Dashboard wäre dies ein Icon, hier als Text-Symbol)
                    print(f"  [ALERT] {alert['player']} ({alert['role']}) isoliert! [SKULL: DEATH PREDICTED]")
                    print(f"    Distanz Ally: {alert['dist_ally']} | Distanz Enemy: {alert['dist_enemy']}")
            else:
                print("  Status: Formation stabil.")

if __name__ == "__main__":
    run_analysis()
