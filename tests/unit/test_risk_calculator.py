from backend.engines.risk_calculator import calculate_risk_score, classify_risk_stage

def test_calculate_risk_score_even():
    state = {
        'gold_diff': 0,
        'team_objectives': {},
        'enemy_objectives': {},
        'team_vision': 1.0,
        'enemy_vision': 1.0
    }
    score = calculate_risk_score(state)
    assert 45 <= score <= 55

def test_calculate_risk_score_winning():
    state = {
        'gold_diff': 10000,
        'team_objectives': {'barons': 1},
        'enemy_objectives': {},
        'team_vision': 2.0,
        'enemy_vision': 1.0
    }
    score = calculate_risk_score(state)
    assert score > 70

def test_classify_risk_stage():
    assert classify_risk_stage(90) == "WINNING"
    assert classify_risk_stage(50) == "COMPETITIVE"
    assert classify_risk_stage(30) == "VULNERABLE"
    assert classify_risk_stage(10) == "CRITICAL"
