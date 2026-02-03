import math

# Konstanten
ISOLATION_THRESHOLD = 3500
CARRIES = ["mid", "adc"]

# Schwellenwerte für den Lonely Carry Index
LCI_ALLY_DIST = 1000
LCI_ENEMY_DIST = 1400

# Teamfight Detection Constants
TF_PLAYER_DISTANCE = 2000
TF_MIN_PLAYERS_PER_TEAM = 3

# Normalisierungsfaktor für den Cohesion Score
COHESION_SPREAD_MAX = 2500 

def get_distance(p1, p2):
    """Berechnet die euklidische Distanz."""
    return math.sqrt((p2['x'] - p1['x'])**2 + (p2['y'] - p1['y'])**2)

def calculate_cohesion_score(player_positions):
    """
    Berechnet die Formation Integrity (Cohesion Score).
    """
    if not player_positions or len(player_positions) < 2:
        return 100.0

    avg_x = sum(p['x'] for p in player_positions) / len(player_positions)
    avg_y = sum(p['y'] for p in player_positions) / len(player_positions)

    total_dist = 0
    for p in player_positions:
        dist = math.sqrt((p['x'] - avg_x)**2 + (p['y'] - avg_y)**2)
        total_dist += dist
    
    avg_spread = total_dist / len(player_positions)
    score = max(0, 100 - (avg_spread / COHESION_SPREAD_MAX * 100))
    return round(score, 2)

def detect_teamfight(all_players_by_team):
    """
    Erkennt einen Teamfight basierend auf der Proximity der Spieler.
    """
    if len(all_players_by_team) < 2:
        return False
        
    blue_team = all_players_by_team[0]
    red_team = all_players_by_team[1]
    
    blue_near_red = 0
    for b in blue_team:
        for r in red_team:
            if get_distance(b, r) < TF_PLAYER_DISTANCE:
                blue_near_red += 1
                break
                
    red_near_blue = 0
    for r in red_team:
        for b in blue_team:
            if get_distance(r, b) < TF_PLAYER_DISTANCE:
                red_near_blue += 1
                break
                
    return blue_near_red >= TF_MIN_PLAYERS_PER_TEAM and red_near_blue >= TF_MIN_PLAYERS_PER_TEAM

def analyze_isolation(own_team, enemy_team):
    """
    Analysiert Spieler-Isolation (Lonely Carry Index).
    """
    alerts = []
    for p in own_team:
        # Heuristik: Rollen-Zuweisung falls nicht vorhanden
        role = p.get('role', 'adc' if 'adc' in p['name'].lower() or 'mid' in p['name'].lower() else 'other')
        
        # Falls keine Rolle explizit da ist, nehmen wir alle als potenzielle Carries für die Demo
        min_ally_dist = min([get_distance(p, a) for a in own_team if a['id'] != p['id']], default=9999)
        min_enemy_dist = min([get_distance(p, e) for e in enemy_team], default=9999)
        
        if min_ally_dist > LCI_ALLY_DIST and min_enemy_dist < LCI_ENEMY_DIST:
            alerts.append({
                "player": p['name'],
                "role": role,
                "dist_ally": round(min_ally_dist, 1),
                "dist_enemy": round(min_enemy_dist, 1)
            })
    return alerts
