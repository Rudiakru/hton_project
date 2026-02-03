from backend.engines.insight_generator import generate_coaching_insights

def test_generate_cohesion_insight():
    analytics = {
        "cohesion_history": [
            {"game_time": "10:00", "cohesion_score": 80},
            {"game_time": "10:10", "cohesion_score": 82},
            {"game_time": "10:20", "cohesion_score": 40} # Drop
        ],
        "risk_score": 20,
        "pattern_history": []
    }
    insights = generate_coaching_insights(analytics)
    assert any(i['type'] == 'COHESION' for i in insights)

def test_generate_risk_insight():
    analytics = {
        "cohesion_history": [],
        "risk_score": 75, # High
        "pattern_history": []
    }
    insights = generate_coaching_insights(analytics)
    assert any(i['type'] == 'RISK' for i in insights)

def test_generate_vision_insight():
    analytics = {
        "cohesion_history": [],
        "risk_score": 20,
        "pattern_history": [
            {"game_time": "15:00", "pattern": {"id": "river_control_loss"}}
        ]
    }
    insights = generate_coaching_insights(analytics)
    assert any(i['type'] == 'VISION' for i in insights)
