import json
import os
import random

def generate_mock_timeline():
    OUTPUT_PATH = "data/processed/risk_timeline.json"
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    timeline = []
    # 20 Minuten Spielzeit, alle 10 Sekunden ein Snapshot
    duration_ms = 20 * 60 * 1000 
    interval_ms = 10000
    
    current_risk = 10
    
    for t in range(0, duration_ms, interval_ms):
        # Zufällige Schwankung mit Trend
        change = random.randint(-5, 7)
        current_risk = max(5, min(95, current_risk + change))
        
        # Ein paar "High Risk" Phasen einbauen
        if 600000 <= t <= 750000: # 10-12.5 min
            current_risk = max(60, current_risk)
        if 840000 <= t <= 860000: # 14:00-14:20 min (Match with validate_risk.py)
            current_risk = max(85, current_risk)
        if 1000000 <= t <= 1100000: # 16.5-18.5 min
            current_risk = max(80, current_risk)

        minutes = t // 60000
        seconds = (t % 60000) // 1000
        
        timeline.append({
            "timestamp": t,
            "game_time": f"{minutes:02d}:{seconds:02d}",
            "risk_score": current_risk,
            "is_teamfight": random.random() < 0.1, # 10% Chance für TF
            "isolation_events": []
        })
        
        # Isolation Alerts bei hohem Risiko hinzufügen
        if current_risk > 70:
            timeline[-1]["isolation_events"].append({
                "player": "Jackies",
                "role": "mid",
                "coords": [random.randint(5000, 10000), random.randint(5000, 10000)]
            })

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(timeline, f, indent=2)
    
    print(f"[OK] Mock-Timeline mit {len(timeline)} Frames generiert: {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_mock_timeline()
