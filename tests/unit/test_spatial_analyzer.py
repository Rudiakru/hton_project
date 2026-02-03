from backend.engines.spatial_analyzer import calculate_cohesion_score, detect_teamfight, get_distance

def test_get_distance():
    p1 = {'x': 0, 'y': 0}
    p2 = {'x': 3, 'y': 4}
    assert get_distance(p1, p2) == 5.0

def test_calculate_cohesion_score_compact():
    players = [{'x': 1000, 'y': 1000}, {'x': 1100, 'y': 1100}]
    score = calculate_cohesion_score(players)
    assert score > 90

def test_calculate_cohesion_score_spread():
    players = [{'x': 1000, 'y': 1000}, {'x': 5000, 'y': 5000}]
    score = calculate_cohesion_score(players)
    assert score < 50

def test_detect_teamfight():
    blue_team = [{'x': 1000, 'y': 1000}, {'x': 1100, 'y': 1100}, {'x': 1200, 'y': 1200}]
    red_team = [{'x': 1050, 'y': 1050}, {'x': 1150, 'y': 1150}, {'x': 1250, 'y': 1250}]
    assert detect_teamfight([blue_team, red_team])

def test_detect_teamfight_no_tf():
    blue_team = [{'x': 1000, 'y': 1000}, {'x': 1100, 'y': 1100}]
    red_team = [{'x': 5000, 'y': 5000}, {'x': 5100, 'y': 5100}]
    assert not detect_teamfight([blue_team, red_team])
