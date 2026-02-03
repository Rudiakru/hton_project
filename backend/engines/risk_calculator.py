
# Heuristic Weights
WEIGHTS = {
    'gold_diff_normalized': 0.4,
    'objective_diff': 0.3,
    'vision_score_ratio': 0.3
}

def normalize_gold_diff(gold_diff, max_diff=15000):
    """
    Normalisiert den Gold-Unterschied auf eine Skala von -1 bis +1.
    """
    return max(-1.0, min(1.0, gold_diff / max_diff))

def calculate_objective_score(dragons, barons, towers):
    """
    Berechnet einen Score basierend auf den kontrollierten Objectives.
    """
    # Heuristische Gewichtung der Objectives
    score = (dragons * 1000) + (barons * 3000) + (towers * 500)
    return score

def calculate_risk_score(game_state):
    """
    Berechnet den Risiko-Score (0-100) basierend auf dem Spielzustand.
    game_state: {
        'gold_diff': int,
        'team_objectives': {'dragons': int, 'barons': int, 'towers': int},
        'enemy_objectives': {'dragons': int, 'barons': int, 'towers': int},
        'team_vision': float,
        'enemy_vision': float
    }
    """
    # 1. Gold Differenz (40%)
    gold_norm = normalize_gold_diff(game_state.get('gold_diff', 0))
    
    # 2. Objectives (30%)
    team_obj = game_state.get('team_objectives', {})
    enemy_obj = game_state.get('enemy_objectives', {})
    
    team_obj_score = calculate_objective_score(
        team_obj.get('dragons', 0), 
        team_obj.get('barons', 0), 
        team_obj.get('towers', 0)
    )
    enemy_obj_score = calculate_objective_score(
        enemy_obj.get('dragons', 0), 
        enemy_obj.get('barons', 0), 
        enemy_obj.get('towers', 0)
    )
    
    obj_diff = (team_obj_score - enemy_obj_score) / 10000 # Normalisierung auf ca. -1 bis 1
    obj_diff = max(-1.0, min(1.0, obj_diff))
    
    # 3. Vision (30%)
    team_vis = game_state.get('team_vision', 1.0)
    enemy_vis = game_state.get('enemy_vision', 1.0)
    if enemy_vis == 0:
        enemy_vis = 0.1
    
    vis_ratio = (team_vis / enemy_vis)
    vis_score = max(-1.0, min(1.0, (vis_ratio - 1.0) / 2.0)) # Normalisierung um 1.0 herum

    # Gesamter Score (-1 bis 1)
    total_score_norm = (
        WEIGHTS['gold_diff_normalized'] * gold_norm +
        WEIGHTS['objective_diff'] * obj_diff +
        WEIGHTS['vision_score_ratio'] * vis_score
    )
    
    # Umwandlung auf 0-100 Skala (0=Kritisch/Verloren, 100=Sicherer Sieg)
    risk_score = (total_score_norm + 1.0) * 50
    return round(max(0.0, min(100.0, risk_score)), 2)

def classify_risk_stage(risk_score):
    """
    Klassifiziert das Risiko in 4 Stufen.
    """
    if risk_score >= 60:
        return "WINNING"
    if risk_score >= 40:
        return "COMPETITIVE"
    if risk_score >= 20:
        return "VULNERABLE"
    return "CRITICAL"
