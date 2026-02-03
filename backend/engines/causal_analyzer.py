# Predefined Impact Weights
EVENT_IMPACTS = {
    "dragon_lost": -6,
    "baron_lost": -12,
    "tower_lost": -3,
    "inhibitor_lost": -7,
    "death_carry": -4,
    "death_support": -2,
    "death_tank": -3,
    "ace": -10,
    "gold_swing_1k": -2,
    "dragon_secured": 6,
    "baron_secured": 12,
    "tower_secured": 3,
    "kill_carry": 4,
    "isolation_risk": -5
}

def build_causal_chain(events, wp_delta, time_window_seconds=60):
    """
    Erklärt eine Änderung der Gewinnwahrscheinlichkeit (WP) durch gewichtete Events.
    events: Liste von dicts mit {'type': str, 'timestamp': int}
    wp_delta: Die beobachtete Änderung des Risk-Scores
    """
    if abs(wp_delta) < 1.0:
        return []

    # Sortiere Events nach Impact-Stärke
    sorted_events = sorted(events, key=lambda e: abs(EVENT_IMPACTS.get(e['type'], 0)), reverse=True)
    
    chain = []
    explained_delta = 0
    
    for event in sorted_events:
        impact = EVENT_IMPACTS.get(event['type'], 0)
        if (wp_delta < 0 and impact < 0) or (wp_delta > 0 and impact > 0):
            chain.append({
                "cause": event['type'].replace('_', ' ').title(),
                "impact": impact,
                "timestamp": event.get('timestamp')
            })
            explained_delta += impact
            
            # Stop wenn wir nah genug an der beobachteten Änderung sind
            if abs(explained_delta - wp_delta) < 2.0:
                break
    
    # Fallback wenn keine Events die Änderung erklären
    if not chain and abs(wp_delta) > 2.0:
        chain.append({
            "cause": "Gradual Map Pressure / Gold Deficit" if wp_delta < 0 else "Gradual Scaling",
            "impact": round(wp_delta, 1)
        })
        
    return chain
